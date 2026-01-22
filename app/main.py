import uvloop
import asyncio
from fastapi import FastAPI
from app.api.v1.rag import router as rag_router
from app.api.v1.health import router as health_router
from app.api.v1.ingestion import router as ingestion_router
from app.api.v1.retreival import router as retrieval_router

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

app = FastAPI(title="RAG")

app.include_router(rag_router, prefix="/api/v1", tags=["Rag"])
app.include_router(health_router, prefix="/api/v1", tags=["Health"])
app.include_router(ingestion_router, prefix="/api/v1", tags=["Vector Indexes"])
app.include_router(retrieval_router, prefix="/api/v1", tags=["Retrieval"])

if __name__ == "__main__":
    # gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
    pass