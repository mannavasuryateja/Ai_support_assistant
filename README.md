# AI-Powered Support Assistant with Endee Vector Database

An intelligent customer support system that uses **semantic vector search** to match user queries with relevant historical support tickets and generate contextual responses.

---

## Problem Statement

Traditional keyword-based support systems fail when users describe problems in their own words. A user typing *"my card got rejected"* and a ticket titled *"Payment failed during checkout"* should match — but keyword search misses this.

This system solves that by converting support queries and tickets into vector embeddings and finding semantically similar cases using Endee's HNSW index.

---

## System Architecture

```
User Query
    │
    ▼
FastAPI (/api/v1/query)
    │
    ▼
SupportAssistant (orchestrator)
    ├── EmbeddingService       → all-MiniLM-L6-v2 (384-dim vectors)
    ├── EndeeClient            → upsert / query via Endee SDK
    │       └── Endee DB       → HNSW index, cosine similarity
    └── ConversationalLLM      → response built from matched ticket context
    │
    ▼
Structured Response
{ action, response, confidence, similar_tickets, processing_time }
```

---

## How Endee Is Used

Endee is the vector database that stores ticket embeddings and answers similarity queries.

**Create index on startup:**
```python
client.create_index(
    name="support_tickets",
    dimension=384,
    space_type="cosine",
    precision=Precision.INT8
)
```

**Upsert ticket embeddings:**
```python
index.upsert([{
    "id": "ticket_001",
    "vector": embedding,       # 384-dim float array
    "meta": {
        "title": "Payment failed during checkout",
        "category": "billing",
        "resolution": "User switched to a different payment method."
    }
}])
```

**Semantic search at query time:**
```python
results = index.query(vector=query_embedding, top_k=5)
# Returns: [{"id": ..., "similarity": 0.87, "meta": {...}}]
```

Tickets scoring above `SIMILARITY_THRESHOLD` (default `0.3`) are passed to the response generator as context.

**Fallback:** If Endee is unreachable at startup, the system automatically switches to `LocalVectorStore` — a pure Python in-memory cosine similarity store — so the app remains fully functional with no code changes required.

---

## Project Structure

```
ai_support_system/
├── app.py                        # FastAPI entry point + HTML chat UI
├── config.py                     # Environment-based configuration
├── requirements.txt
├── .env                          # Local config (not committed)
├── .env.example                  # Template
├── src/
│   ├── support_assistant.py      # Main pipeline orchestrator
│   ├── api/
│   │   ├── routes.py             # REST API endpoints
│   │   └── models.py             # Pydantic request/response models
│   ├── embeddings/
│   │   ├── embedding_service.py  # Sentence Transformers wrapper
│   │   └── simple_embedding.py   # TF-IDF fallback embedder
│   ├── vector_store/
│   │   ├── endee_client.py       # Endee SDK client
│   │   └── local_vector_store.py # In-memory fallback
│   └── llm/
│       └── conversational_llm.py # Response generation
└── docker-compose.yml
```

---

## Setup & Running

### Prerequisites
- Python 3.8+
- Docker Desktop

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ai_support_system.git
cd ai_support_system
```

### 2. Create virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

`.env` settings:
```env
ENDEE_URL=http://localhost:8080
ENDEE_API_KEY=
ENDEE_COLLECTION_NAME=support_tickets
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
SIMILARITY_THRESHOLD=0.3
MAX_RESULTS=5
API_HOST=0.0.0.0
API_PORT=8000
```

### 5. Start Endee vector database

```bash
docker run -d \
  --name endee-support-db \
  -p 8080:8080 \
  -v endee_data:/data \
  endeeio/endee-server:latest
```

Verify Endee is running:
```bash
curl http://localhost:8080/api/v1/health
```

### 6. Run the application

```bash
python app.py
```

Open: **http://localhost:8000**

On startup the system will:
- Connect to Endee and create the `support_tickets` index
- Embed 8 sample tickets and upsert them into Endee
- Begin serving queries through the chat UI and REST API

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Chat UI |
| `POST` | `/api/v1/query` | Submit a support query |
| `POST` | `/api/v1/tickets` | Batch insert tickets |
| `POST` | `/api/v1/tickets/single` | Insert a single ticket |
| `GET` | `/api/v1/health` | System health |
| `GET` | `/api/v1/stats` | System statistics |
| `GET` | `/api/v1/search/{query}` | Raw vector search |
| `GET` | `/docs` | Swagger UI |

**Example query:**
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "My payment failed during checkout", "max_results": 3}'
```

**Response:**
```json
{
  "action": "solution",
  "response": "Based on similar payment issues, here are steps that often help...",
  "confidence": 0.85,
  "similar_tickets": [...],
  "processing_time": 0.05
}
```

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ENDEE_URL` | `http://localhost:8080` | Endee server URL |
| `ENDEE_API_KEY` | `` | Auth token (leave empty if auth disabled) |
| `ENDEE_COLLECTION_NAME` | `support_tickets` | Index name in Endee |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence Transformers model |
| `EMBEDDING_DIMENSION` | `384` | Vector dimension |
| `SIMILARITY_THRESHOLD` | `0.3` | Minimum similarity score to use a result |
| `MAX_RESULTS` | `5` | Top-K results returned from Endee |

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Endee unavailable` at startup | Run `docker start endee-support-db` |
| `0/8 tickets inserted` | Check `docker logs endee-support-db` |
| `sentence-transformers unavailable` | Run `pip install sentence-transformers` |
| Browser shows `ERR_ADDRESS_INVALID` | Open `localhost:8000`, not `0.0.0.0:8000` |
| Port 8080 already allocated | Run `docker ps` and stop the conflicting container |

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Vector Database | [Endee](https://endee.io) |
| Embeddings | [Sentence Transformers](https://www.sbert.net/) — `all-MiniLM-L6-v2` |
| API Framework | [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn |
| Containerisation | Docker |

---

## License

MIT
