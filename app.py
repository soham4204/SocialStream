import logging
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from neo4j_client import Neo4jClient
import uvicorn
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# --- Pydantic Models for Request Validation ---

class Interaction(BaseModel):
    """
    Defines the structure for an incoming interaction event.
    """
    user1: str = Field(..., description="The name of the user initiating the interaction.")
    user2: str = Field(..., description="The name of the user receiving the interaction.")
    interaction_type: str = Field(..., description="The type of interaction (e.g., LIKE, FOLLOW, COMMENT).")

    class Config:
        json_schema_extra = {
            "example": {
                "user1": "Alice",
                "user2": "Bob",
                "interaction_type": "LIKE"
            }
        }

# --- FastAPI App Initialization ---

app = FastAPI(
    title="Social Interaction API",
    description="API to log user interactions to a Neo4j database.",
    version="1.0.0"
)

# --- Database Dependency ---

# This is a simple dependency injection setup.
# It creates a single client instance and yields it for requests.
def get_neo4j_client():
    """
    Dependency injector that creates and yields a Neo4jClient.
    This function will be called once per request that needs it.
    """
    client = None
    try:
        client = Neo4jClient()
        yield client
    except Exception as e:
        logging.error("Failed to create Neo4j client: %s", e)
        raise HTTPException(status_code=503, detail="Could not connect to the database.")
    finally:
        if client:
            client.close()

# --- API Endpoints ---

@app.get("/health", tags=["Monitoring"])
async def health_check():
    """
    Simple health check endpoint to verify the API is running.
    """
    logging.info("Health check endpoint was hit.")
    return {"status": "ok"}

@app.post("/interaction", status_code=201, tags=["Interactions"])
async def log_interaction(
    interaction: Interaction, 
    client: Neo4jClient = Depends(get_neo4j_client)
):
    """
    Receives an interaction event and logs it to the Neo4j database.
    This is the endpoint the Kafka Consumer will call.
    """
    try:
        logging.info("Received interaction: %s", interaction.model_dump_json())
        client.add_interaction(
            user1_name=interaction.user1,
            user2_name=interaction.user2,
            interaction_type=interaction.interaction_type
        )
        return {"status": "success", "data": interaction}
    except Exception as e:
        logging.error("Error processing interaction: %s", e)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/interactions", tags=["Interactions"])
async def get_interactions(client: Neo4jClient = Depends(get_neo4j_client)):
    """
    Fetches all nodes and relationships from the Neo4j database.
    This is the endpoint the Streamlit Dashboard will call.
    """
    try:
        nodes, edges = client.get_all_interactions()
        return {"nodes": nodes, "edges": edges}
    except Exception as e:
        logging.error("Error getting interactions: %s", e)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# --- Main entry point for running with uvicorn ---
if __name__ == "__main__":
    load_dotenv()
    host = os.getenv("FASTAPI_HOST", "localhost")
    port = int(os.getenv("FASTAPI_PORT", 8000))
    logging.info("Starting FastAPI server on %s:%d", host, port)
    uvicorn.run(app, host=host, port=port)