import os
import logging
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class Neo4jClient:
    """
    A client for interacting with the Neo4j database.
    Handles connection, data insertion, and querying.
    """

    def __init__(self):
        """
        Initializes the client and connects to the Neo4j database
        using credentials from the .env file.
        """
        load_dotenv()
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")
        
        if not all([uri, user, password]):
            logging.error("Neo4j credentials not found in .env file.")
            raise ValueError("NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set")

        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.driver.verify_connectivity()
            logging.info("Successfully connected to Neo4j database at %s", uri)
        except Exception as e:
            logging.error("Failed to connect to Neo4j: %s", e)
            raise

    def close(self):
        """Closes the Neo4j database driver connection."""
        if self.driver:
            self.driver.close()
            logging.info("Neo4j connection closed.")

    def add_interaction(self, user1_name: str, user2_name: str, interaction_type: str):
        """
        Creates two User nodes (if they don't exist) and adds a
        relationship between them representing an interaction.
        """
        # Using MERGE ensures we don't create duplicate users
        # Using MERGE for the relationship ensures we don't create duplicate interactions
        # (or, we could update properties if it already exists)
        
        # Here, we'll allow multiple identical interactions (e.g., 'Alice LIKES Bob'
        # can happen many times). So we'll MERGE users and CREATE the relationship.
        
        query = (
            "MERGE (u1:User {name: $user1_name}) "
            "MERGE (u2:User {name: $user2_name}) "
            "CREATE (u1)-[r:INTERACTED {type: $interaction_type, timestamp: datetime()}]->(u2) "
            "RETURN type(r) AS interaction, u1.name AS from_user, u2.name AS to_user"
        )
        
        try:
            with self.driver.session() as session:
                result = session.run(query, user1_name=user1_name, user2_name=user2_name, interaction_type=interaction_type)
                record = result.single()
                if record:
                    logging.info("Added interaction: %s -[%s]-> %s", record['from_user'], record['interaction'], record['to_user'])
                else:
                    logging.warning("Interaction was created but no record returned.")
        except Exception as e:
            logging.error("Error adding interaction to Neo4j: %s", e)

    def get_all_interactions(self):
        """
        Fetches all user nodes and their interactions to build the graph.
        Returns a list of nodes and a list of relationships.
        """
        query = """
        MATCH (u1:User)-[r:INTERACTED]->(u2:User)
        RETURN u1.name AS user1, u2.name AS user2, r.type AS type
        """
        nodes = set()
        edges = []
        try:
            with self.driver.session() as session:
                results = session.run(query)
                for record in results:
                    user1 = record['user1']
                    user2 = record['user2']
                    nodes.add(user1)
                    nodes.add(user2)
                    edges.append({"source": user1, "target": user2, "label": record['type']})
            
            # Convert set of nodes to list of dicts for consistency
            node_list = [{"id": name} for name in nodes]
            logging.info("Fetched %d nodes and %d edges", len(node_list), len(edges))
            return node_list, edges
        except Exception as e:
            logging.error("Error fetching interactions from Neo4j: %s", e)
            return [], [] # Return empty lists on failure