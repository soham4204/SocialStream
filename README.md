<div align="center">
  <h1>🚀 Real-Time Social Interaction Network</h1>
  <p>An end-to-end, real-time event streaming and visualization architecture for social networks — using Python, Kafka, Neo4j, FastAPI, and Streamlit. Connect the dots, see your data flow live! 🌐</p>
  
  <p>
    <!-- Tech Logos -->
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" alt="Python" width="40"/>
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg" alt="FastAPI" width="40"/>
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/apachekafka/apachekafka-original.svg" alt="Kafka" width="40"/>
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/neo4j/neo4j-original.svg" alt="Neo4j" width="40"/>
    <img src="https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.svg" alt="Streamlit" width="110"/>
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg" alt="Docker" width="45" style="margin-bottom:-7px;"/>
  </p>

  <p><strong>Live, Interactive, Beautiful</strong></p>
</div>

---

## 📊 Dashboard Preview

<p align="center">
  <!-- REPLACE the link below with a PNG/GIF screenshot of your app (drag image to GitHub issue to upload and get link) -->
  <img src="YOUR_SCREENSHOT_URL_HERE" alt="Dashboard Screenshot" width="70%">
</p>
<p align="center">*(Add a screenshot or GIF of your <code>dashboard.py</code> here)*</p>

---

## 🏛️ Architecture Overview

> **Data Flow:**
>
> 🧑‍🔬 <b>Producer</b> → 🔥 <b>Kafka Topic</b> → 👷 <b>Consumer</b> → 🚦 <b>FastAPI</b> → 🌳 <b>Neo4j</b> ↔️ <b>Streamlit Dashboard</b> 🌐

```
(Producer) ─→ [Kafka Topic] ─→ (Consumer) ─→ (FastAPI API) ─→ (Neo4j DB)
                                        ↑
                               (Streamlit UI)
```

* **Event Simulation:** `kafka_producer.py` generates random social actions (e.g., "Alice LIKES Bob").
* **Kafka Streaming:** Sends events to the `user_interactions` topic.
* **Worker/Consumer:** `kafka_consumer.py` ingests events, forwards to FastAPI.
* **API Backend:** `app.py` (FastAPI) accepts and writes data to Neo4j.
* **Graph Database:** Neo4j represents users as nodes, interactions as relationships.
* **Frontend:** `dashboard.py` (Streamlit) fetches data from FastAPI and visualizes with Pyvis/NetworkX; auto-updates every 5s.

---

## 🚦 Tech Stack & Tools

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-005571?logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/Apache_Kafka-231F20?logo=apache-kafka&logoColor=white"/>
  <img src="https://img.shields.io/badge/Neo4j-008CC1?logo=neo4j&logoColor=white"/>
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/pyvis-3776AB?logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white"/>
</p>

---

## 🏃‍♂️ Getting Started

#### 🔗 Prerequisites
- Python 3.9+
- Docker & Docker Compose

### 1️⃣ Installation

1. **Clone the repo:**
    ```bash
    git clone https://github.com/soham4204/SocialStream.git
    cd social-network-stream
    ```
2. **Create virtual environment:**
    ```bash
    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```
3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4. **Add environment config:** Create a `.env` file with:
    ```ini
    NEO4J_URI=bolt://localhost:7687
    NEO4J_USER=neo4j
    NEO4J_PASSWORD=password
    KAFKA_BOOTSTRAP_SERVERS=localhost:9092
    FASTAPI_HOST=localhost
    FASTAPI_PORT=8000
    KAFKA_TOPIC=user_interactions
    ```

### 2️⃣ Running the Application (each in a different terminal)

**1. Infrastructure (Kafka & Neo4j)**
```bash
docker-compose up -d
```
*Wait 30-60 seconds for the services to initialize.*

**2. FastAPI Backend**
```bash
uvicorn app:app --host localhost --port 8000
```

**3. Kafka Producer**
```bash
python kafka_producer.py
```

**4. Kafka Consumer**
```bash
python kafka_consumer.py
```

**5. Streamlit Dashboard**
```bash
streamlit run dashboard.py
```

### 3️⃣ Verification
- 🕸️ Visit [localhost:8501](http://localhost:8501) for the Streamlit app
- 🌀 Visit [localhost:7474](http://localhost:7474) for Neo4j Browser (login: `neo4j`/`password`)
- ⚡ Visit [localhost:8000/docs](http://localhost:8000/docs) for FastAPI auto-generated docs

---

## 📁 Directory Structure

```text
social-network-stream/
├── .env                  # Secrets and configuration
├── docker-compose.yml    # Compose file for Kafka, Zookeeper, Neo4j
├── requirements.txt      # Python dependencies
├── README.md             # This file
├── app.py                # FastAPI backend
├── neo4j_client.py       # Neo4j helper client
├── kafka_producer.py     # Event simulator
├── kafka_consumer.py     # Kafka → FastAPI pipeline worker
└── dashboard.py          # Streamlit dashboard
```

---

## 🛠️ Troubleshooting & FAQ

| 🛑 Issue | ✔️ Solution |
| ------ | ----------- |
| Kafka connection refused | Wait for Kafka/Zookeeper to finish starting (30-60s). |
| Neo4j authentication failed | Ensure password in `.env` & `docker-compose.yml` match. |
| Consumer not receiving messages | Topic mismatch? Ensure `KAFKA_TOPIC` is set identically. |
| Streamlit not updating | Check backend is running and reload dashboard. |
| Port already in use | Stop previous process or pick a new port in `.env`. |

---

## ✨ Future Extensions

- 🔄 **WebSocket-powered dashboard** (replace polling)
- 💬 **Sentiment analysis visualization** (color edges by mood)
- ⏳ **Time series view** for trend analytics
- 🌟 **Top influencers leaderboard**
- 🔐 **User authentication**
- ☁️ **Cloud-native deployment & CI/CD**

---

<div align="center">
  <strong>🎉 This concludes the local development & documentation. Ready for worldwide deployment? Ask for the <em>Free Deployment Plan</em>! 🚀</strong>
</div>


