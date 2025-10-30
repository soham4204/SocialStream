import streamlit as st
import requests
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import logging

# --- Page Configuration ---
st.set_page_config(
    page_title="Real-Time Social Interaction Network",
    page_icon="🕸️",
    layout="wide",
)

# --- Constants ---
API_URL = "http://localhost:8000/interactions"

# --- Logging ---
logging.basicConfig(level=logging.INFO)

# --- Data Fetching ---
def fetch_data():
    """Fetches graph data from the FastAPI backend."""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        return data.get("nodes", []), data.get("edges", [])
    except requests.exceptions.ConnectionError:
        st.error(f"Connection Error: Is the FastAPI server running at {API_URL}?")
        return None, None
    except Exception as e:
        st.error(f"An error occurred while fetching data: {e}")
        return None, None

# --- Main Application ---
st.title("🕸️ Real-Time Social Interaction Network")
st.write("Visualizing live user interactions streamed via Kafka and stored in Neo4j.")

# --- Fetch Data ---
nodes, edges = fetch_data()

if nodes is None or edges is None:
    st.warning("Could not load data. See error above.")
else:
    # --- Sidebar for Metrics and Filters ---
    st.sidebar.header("📊 Dashboard")
    
    # 1. Metrics
    total_users = len(nodes)
    total_interactions = len(edges)
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric(label="Total Users", value=total_users)
    with col2:
        st.metric(label="Total Interactions", value=total_interactions)

    # 2. Filters
    st.sidebar.header("🔍 Filters")
    all_types = sorted(list(set(edge['label'] for edge in edges)))
    
    selected_types = st.sidebar.multiselect(
        "Filter by interaction type:",
        options=all_types,
        default=all_types
    )

    if not selected_types:
        st.warning("Please select at least one interaction type to display.")
    else:
        # --- Filter Data ---
        filtered_edges = [edge for edge in edges if edge['label'] in selected_types]
        # Get all unique nodes from the filtered edges
        filtered_nodes = set()
        for edge in filtered_edges:
            filtered_nodes.add(edge['source'])
            filtered_nodes.add(edge['target'])
    
        # --- Build the Graph ---
        # We must use DiGraph for directed interactions like 'FOLLOWS'
        G = nx.DiGraph()

        for node in filtered_nodes:
            G.add_node(node)
            
        for edge in filtered_edges:
            G.add_edge(edge['source'], edge['target'], label=edge['label'], title=edge['label'])

        # --- Generate Pyvis Visualization ---
        net = Network(height="700px", width="100%", heading="", directed=True, notebook=False)
        net.from_nx(G)
        
        # Add physics-based layout controls
        net.show_buttons(filter_=['physics'])

        # Save the graph to an HTML file
        try:
            net.save_graph("graph.html")
            
            # Read the HTML file
            with open("graph.html", "r", encoding="utf-8") as f:
                source_code = f.read()
            
            # Display the HTML in Streamlit
            components.html(source_code, height=710)
            
        except Exception as e:
            st.error(f"Error generating graph: {e}")

# --- Auto-Refresh ---
st.rerun(ttl=5)