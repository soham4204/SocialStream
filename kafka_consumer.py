import os
import logging
import time
import json
import requests
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def connect_to_kafka(bootstrap_servers, topic):
    """
    Continuously attempts to connect to Kafka until successful.
    """
    consumer = None
    while not consumer:
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=bootstrap_servers,
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                auto_offset_reset='earliest', # Start reading from the beginning
                group_id='social-stream-workers' # Consumer group ID
            )
            logging.info("Kafka Consumer connected successfully.")
            return consumer
        except NoBrokersAvailable:
            logging.warning("Kafka broker not available. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            logging.error(f"An unexpected error occurred connecting to Kafka: {e}")
            time.sleep(5)

def post_to_api(interaction_data, api_url):
    """
    Posts data to the FastAPI endpoint with retry logic.
    """
    while True:
        try:
            response = requests.post(api_url, json=interaction_data)
            response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
            logging.info(f"Successfully posted to API: {interaction_data}")
            return True
        except requests.exceptions.ConnectionError:
            logging.warning(f"FastAPI server at {api_url} not reachable. Retrying in 5 seconds...")
            time.sleep(5)
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP Error posting to API: {e.response.status_code} {e.response.text}")
            # Don't retry on client error (e.g., 400 Bad Request), but do retry on server error (5xx)
            if 400 <= e.response.status_code < 500:
                logging.error("Client error, message will be skipped.")
                return False # Stop retrying
            time.sleep(5) # Retry on server errors
        except Exception as e:
            logging.error(f"An unexpected error occurred posting to API: {e}")
            time.sleep(5)

def main():
    """Main function to run the consumer."""
    load_dotenv()
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    topic = os.getenv("KAFKA_TOPIC")
    fastapi_host = os.getenv("FASTAPI_HOST")
    fastapi_port = os.getenv("FASTAPI_PORT")

    if not all([bootstrap_servers, topic, fastapi_host, fastapi_port]):
        logging.error("One or more environment variables are not set.")
        return

    api_url = f"http://{fastapi_host}:{fastapi_port}/interaction"
    consumer = connect_to_kafka(bootstrap_servers, topic)

    try:
        logging.info("Consumer is now listening for messages...")
        for message in consumer:
            interaction = message.value
            logging.info(f"Received from Kafka: {interaction}")
            post_to_api(interaction, api_url)
            
    except KeyboardInterrupt:
        logging.info("Consumer shutting down...")
    finally:
        if consumer:
            consumer.close()
            logging.info("Kafka Consumer closed.")

if __name__ == "__main__":
    main()