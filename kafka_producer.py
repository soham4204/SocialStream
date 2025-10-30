import os
import logging
import time
import json
import random
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# --- Sample Data ---
USERS = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy"]
INTERACTIONS = ["LIKE", "COMMENT", "FOLLOW", "SHARE", "MENTION"]
# ---------------------

def connect_to_kafka(bootstrap_servers):
    """
    Continuously attempts to connect to Kafka until successful.
    """
    producer = None
    while not producer:
        try:
            producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            logging.info("Kafka Producer connected successfully.")
            return producer
        except NoBrokersAvailable:
            logging.warning("Kafka broker not available. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            logging.error(f"An unexpected error occurred connecting to Kafka: {e}")
            time.sleep(5)

def generate_event():
    """Generates a random interaction event."""
    user1 = random.choice(USERS)
    user2 = random.choice(USERS)
    
    # Ensure user1 and user2 are not the same
    while user1 == user2:
        user2 = random.choice(USERS)
        
    interaction_type = random.choice(INTERACTIONS)
    
    return {
        "user1": user1,
        "user2": user2,
        "interaction_type": interaction_type
    }

def main():
    """Main function to run the producer."""
    load_dotenv()
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    topic = os.getenv("KAFKA_TOPIC")

    if not all([bootstrap_servers, topic]):
        logging.error("KAFKA_BOOTSTRAP_SERVERS or KAFKA_TOPIC not set in .env")
        return

    producer = connect_to_kafka(bootstrap_servers)

    try:
        while True:
            message = generate_event()
            producer.send(topic, value=message)
            producer.flush() # Ensure message is sent
            logging.info(f"Sent event to topic '{topic}': {message}")
            
            # Wait for a random delay (1-3 seconds) as per your plan
            time.sleep(random.uniform(1, 3))
            
    except KeyboardInterrupt:
        logging.info("Producer shutting down...")
    finally:
        if producer:
            producer.close()
            logging.info("Kafka Producer closed.")

if __name__ == "__main__":
    main()