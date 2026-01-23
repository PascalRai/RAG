# RAG — FastAPI + Celery + Qdrant

Overview
- RAG is a retrieval-augmented generation backend composed of a FastAPI server and a Celery worker that share the same Docker image. Qdrant is used as the vector DB and RabbitMQ as the Celery broker. A Streamlit UI is provided to interact locally.

Project structure (important files)
```
- Dockerfile
- docker-compose.yml
- .env (placed in repository root)
- .dockerignore

app/
- main.py — FastAPI app entry
- api/v1/
  - health.py — health endpoints
  - ingestion.py — ingestion endpoints
  - rag.py, retreival.py — RAG / retrieval endpoints
- core/settings.py — configuration loader
  - utils/ — ingestion/rag/retriever helper utilities
- schemas/ — request/response Pydantic schemas
- services/ingestion/
  - ingestion_task.py — celery app & task entry
  - ingestion_task_pipeline.py, ingestion_task_utils.py — ingestion pipeline helpers
  - celeryconfig.py — celery configuration
```
Components used
- Qdrant — vector database (qdrant/qdrant)
- RabbitMQ — message broker for Celery (rabbitmq:3-management)
- Celery — background worker for ingestion/indexing
- FastAPI — HTTP API (served with Gunicorn + UvicornWorker)
- Streamlit — local UI (run outside Docker)

Environment (.env)
- Place a single `.env` in the RAG directory (shared by fastapi and celery_worker).
- Required: OPENAI_API_KEY
- Other defaults in code should work; example optional variables shown below.

```bash
OPENAI_API_KEY=
# Optional defaults (adjust if needed)
RABBITMQ_USER=user
RABBITMQ_PASS=password
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
CELERY_BROKER_URL=amqp://user:password@rabbitmq:5672//
QDRANT_URL=http://qdrant:6333
```

How to start the app (backend)

From the RAG directory run:
```bash
docker compose up -d --build
```

Note: the image build will download Python packages and large wheels; this can take time or fail on slow networks. Retry if necessary.

Services started by compose:
```
fastapi — web API on port 8000
celery_worker — ingestion/indexing worker
qdrant — vector DB (ports 6333/6334)
rabbitmq — broker (ports 5672/15672)
Streamlit UI (run locally, not in Docker)
```
Create and activate a venv:
```bash
python3 -m venv venv
source venv/bin/activate
```
Install streamlit and run:
```bash
pip install streamlit
streamlit run streamlit.py
```

Indexing files into Qdrant

The ingestion/indexing worker is isolated from the web upload endpoints. For now, upload files by placing them into a shared data/ directory in the repo root. Map that directory as a volume to the celery worker in docker-compose so the worker can read the files and index them into Qdrant.

Example: place files under ./data/ and use the worker-side path in ingestion tasks to start indexing.

Indexing files into Qdrant

The ingestion/indexing worker is isolated from the web upload endpoints. For now, upload files by placing them into a shared data/ directory in the repo root. Map that directory as a volume to the celery worker in docker-compose so the worker can read the files and index them into Qdrant.

Example: place files under ./data/ and use the worker-side path in ingestion tasks to start indexing.

To trigger ingestion via the API, use the following curl command (replace `asdf` with your desired index name and adjust the file path):

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/indexes/asdf/pdf' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "file_path": "data/docs/2022 Q3 AAPL.pdf"
}'
```