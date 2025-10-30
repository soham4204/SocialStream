import streamlit as st
import requests
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import logging
from datetime import datetime
import pandas as pd
from collections import Counter
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="Social Stream Analytics",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Modern Look ---
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --background-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        border-left: 4px solid #667eea;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.12);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.5rem;
    }
    
    /* Graph container */
    .graph-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-top: 1rem;
    }
    
    /* Sidebar styling */
    .sidebar-section {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    /* Status indicator */
    .status-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .status-live {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- Constants ---
API_URL = "http://localhost:8000/interactions"

# --- Logging ---
logging.basicConfig(level=logging.INFO)

# --- Session State Initialization ---
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
if 'update_count' not in st.session_state:
    st.session_state.update_count = 0
if 'graph_layout' not in st.session_state:
    st.session_state.graph_layout = "force_atlas_2based"

# --- Data Fetching ---
@st.cache_data(ttl=5)
def fetch_data():
    """Fetches graph data from the FastAPI backend."""
    try:
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("nodes", []), data.get("edges", []), None
    except requests.exceptions.ConnectionError:
        return None, None, "Connection Error: FastAPI server not reachable"
    except requests.exceptions.Timeout:
        return None, None, "Timeout Error: Server took too long to respond"
    except Exception as e:
        return None, None, f"Error: {str(e)}"

# --- Analytics Functions ---
def calculate_network_metrics(G):
    """Calculate key network metrics."""
    metrics = {}
    
    if len(G.nodes()) > 0:
        metrics['density'] = nx.density(G)
        metrics['avg_degree'] = sum(dict(G.degree()).values()) / len(G.nodes())
        
        # Find most connected users
        degree_centrality = nx.degree_centrality(G)
        metrics['top_users'] = sorted(degree_centrality.items(), 
                                      key=lambda x: x[1], 
                                      reverse=True)[:5]
        
        # Find most influential (by in-degree in directed graph)
        in_degree = dict(G.in_degree())
        metrics['most_followed'] = sorted(in_degree.items(), 
                                         key=lambda x: x[1], 
                                         reverse=True)[:5]
    
    return metrics

def get_interaction_stats(edges):
    """Get statistics about interaction types."""
    interaction_types = [edge['label'] for edge in edges]
    return Counter(interaction_types)

# --- Header ---
st.markdown("""
<div class="main-header">
    <h1>🕸️ Social Network Analytics</h1>
    <p>Real-time visualization of user interactions • Powered by Kafka → Neo4j → FastAPI</p>
</div>
""", unsafe_allow_html=True)

# --- Fetch Data ---
nodes, edges, error = fetch_data()

if error:
    st.error(f"⚠️ {error}")
    st.info("💡 Make sure the FastAPI server is running: `uvicorn app:app --reload`")
    st.stop()

if not nodes or not edges:
    st.warning("📭 No data available yet. Waiting for interactions...")
    st.info("Start the Kafka producer to generate social interactions.")
    time.sleep(5)
    st.rerun()

# Update counter
st.session_state.update_count += 1
st.session_state.last_update = datetime.now()

# --- Sidebar ---
with st.sidebar:
    # Status indicator
    st.markdown(f"""
    <div class="sidebar-section">
        <h3 style="margin:0; color:#667eea;">🔴 Live Dashboard</h3>
        <div class="status-badge status-live">● STREAMING</div>
        <p style="font-size:0.85rem; color:#666; margin-top:0.5rem;">
            Last updated: {st.session_state.last_update.strftime('%H:%M:%S')}<br>
            Updates: {st.session_state.update_count}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key Metrics
    st.markdown("### 📊 Network Overview")
    
    total_users = len(nodes)
    total_interactions = len(edges)
    interaction_stats = get_interaction_stats(edges)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("👥 Users", total_users, delta=None)
    with col2:
        st.metric("💬 Interactions", total_interactions, delta=None)
    
    # Interaction breakdown
    st.markdown("### 📈 Interaction Types")
    for interaction_type, count in interaction_stats.most_common():
        percentage = (count / total_interactions) * 100
        st.progress(percentage / 100)
        st.caption(f"{interaction_type}: {count} ({percentage:.1f}%)")
    
    st.markdown("---")
    
    # Filters
    st.markdown("### 🔍 Filters")
    all_types = sorted(list(set(edge['label'] for edge in edges)))
    
    selected_types = st.multiselect(
        "Interaction Types",
        options=all_types,
        default=all_types,
        help="Select which types of interactions to display"
    )
    
    # Graph layout options
    st.markdown("### ⚙️ Graph Settings")
    
    layout_options = {
        "Force Atlas 2": "force_atlas_2based",
        "Barnes Hut": "barnes_hut",
        "Hierarchical": "hierarchical",
        "Repulsion": "repulsion"
    }
    
    selected_layout = st.selectbox(
        "Layout Algorithm",
        options=list(layout_options.keys()),
        index=0,
        help="Choose how nodes are arranged"
    )
    
    st.session_state.graph_layout = layout_options[selected_layout]
    
    show_physics = st.checkbox("Enable Physics", value=True, 
                               help="Allow nodes to move dynamically")
    
    node_size = st.slider("Node Size", 10, 50, 25)
    
    st.markdown("---")
    
    # Refresh controls
    st.markdown("### 🔄 Refresh Settings")
    auto_refresh = st.checkbox("Auto-refresh", value=True)
    refresh_interval = st.slider("Refresh interval (seconds)", 3, 30, 5)
    
    if st.button("🗑️ Clear Cache", use_container_width=True):
        st.cache_data.clear()
        st.success("Cache cleared!")
        time.sleep(1)
        st.rerun()

# --- Main Content Area ---
if not selected_types:
    st.warning("⚠️ Please select at least one interaction type to display.")
    st.stop()

# Filter data
filtered_edges = [edge for edge in edges if edge['label'] in selected_types]
filtered_nodes = set()
for edge in filtered_edges:
    filtered_nodes.add(edge['source'])
    filtered_nodes.add(edge['target'])

if not filtered_edges:
    st.info("🔍 No interactions match the selected filters.")
    st.stop()

# --- Top Section: Key Analytics ---
col1, col2, col3, col4 = st.columns(4)

# Build NetworkX graph for analytics
G = nx.DiGraph()
for node in filtered_nodes:
    G.add_node(node)
for edge in filtered_edges:
    G.add_edge(edge['source'], edge['target'], label=edge['label'])

metrics = calculate_network_metrics(G)

with col1:
    st.markdown("""
    <div class="metric-card">
        <p class="metric-value">{:.2%}</p>
        <p class="metric-label">Network Density</p>
    </div>
    """.format(metrics.get('density', 0)), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <p class="metric-value">{:.1f}</p>
        <p class="metric-label">Avg Connections</p>
    </div>
    """.format(metrics.get('avg_degree', 0)), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <p class="metric-value">{}</p>
        <p class="metric-label">Active Nodes</p>
    </div>
    """.format(len(filtered_nodes)), unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <p class="metric-value">{}</p>
        <p class="metric-label">Connections</p>
    </div>
    """.format(len(filtered_edges)), unsafe_allow_html=True)

# --- Graph Visualization ---
st.markdown("### 🌐 Network Visualization")

with st.container():
    st.markdown('<div class="graph-container">', unsafe_allow_html=True)
    
    # Create Pyvis network
    net = Network(
        height="650px", 
        width="100%", 
        directed=True, 
        notebook=False,
        bgcolor="#ffffff",
        font_color="#333333"
    )
    
    # Add nodes with custom styling
    for node in filtered_nodes:
        in_degree = G.in_degree(node)
        out_degree = G.out_degree(node)
        
        # Size based on total connections
        size = node_size + (in_degree + out_degree) * 3
        
        # Color based on popularity
        if in_degree > 5:
            color = "#764ba2"  # Purple for popular users
        elif in_degree > 2:
            color = "#667eea"  # Blue for moderately popular
        else:
            color = "#a8b2fa"  # Light blue for others
        
        title = f"{node}<br>Followers: {in_degree}<br>Following: {out_degree}"
        net.add_node(node, label=node, size=size, color=color, title=title)
    
    # Add edges with custom styling
    color_map = {
        'FOLLOWS': '#667eea',
        'LIKES': '#f093fb',
        'COMMENTS_ON': '#4facfe'
    }
    
    for edge in filtered_edges:
        color = color_map.get(edge['label'], '#999999')
        net.add_edge(
            edge['source'], 
            edge['target'], 
            title=edge['label'],
            color=color,
            arrows='to',
            smooth={'type': 'curvedCW', 'roundness': 0.2}
        )
    
    # Configure physics
    if show_physics:
        net.set_options(f"""
        {{
            "physics": {{
                "enabled": true,
                "solver": "{st.session_state.graph_layout}",
                "stabilization": {{
                    "iterations": 100
                }}
            }},
            "interaction": {{
                "hover": true,
                "navigationButtons": true,
                "keyboard": true
            }}
        }}
        """)
    else:
        net.set_options("""
        {
            "physics": {
                "enabled": false
            }
        }
        """)
    
    # Generate and display
    try:
        net.save_graph("graph.html")
        with open("graph.html", "r", encoding="utf-8") as f:
            source_code = f.read()
        components.html(source_code, height=670)
    except Exception as e:
        st.error(f"Error generating graph: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Bottom Section: Analytics Tables ---
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏆 Top Influencers")
    if metrics.get('most_followed'):
        df_influencers = pd.DataFrame(
            metrics['most_followed'],
            columns=['User', 'Followers']
        )
        st.dataframe(
            df_influencers,
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No data available yet")

with col2:
    st.markdown("### 🔥 Most Active Users")
    if metrics.get('top_users'):
        df_active = pd.DataFrame(
            [(user, f"{score:.2%}") for user, score in metrics['top_users']],
            columns=['User', 'Activity Score']
        )
        st.dataframe(
            df_active,
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No data available yet")

# --- Auto-refresh ---
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()