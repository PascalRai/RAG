from qdrant_client import QdrantClient
from fastapi import APIRouter, Depends, HTTPException

from app.core.settings import settings
from app.schemas.ingestion_schema import IngestFilePathRequest
from app.services.ingestion.ingestion_task import ingestion_task
from app.core.utils.ingestion_utils import (
    ensure_collection, 
    delete_collection,
    get_collections
)

router = APIRouter()

def get_qdrant_client() -> QdrantClient:
    try:
        return QdrantClient(url=settings.qdrant_url)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not connect to Qdrant: {str(e)}")

@router.post("/indexes/{index_name}/pdf")
async def ingest_pdf(
    index_name: str,
    request: IngestFilePathRequest,
    client: QdrantClient = Depends(get_qdrant_client)
    ):
    # Ensure the index/collection exists
    result = ensure_collection(client, index_name)
    print(result)

    ingestion_task.delay(
        file_path=request.file_path,
        index_name=index_name
    )
    return {"status": "enqueued", "index": index_name, "file_path": request.file_path}


@router.delete("/indexes/{index_name}")
async def delete_index(
    index_name: str,
    client: QdrantClient = Depends(get_qdrant_client)
    ):
    success = delete_collection(client, index_name)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete index")
    return {"status": "deleted", "index": index_name}


@router.get("/indexes")
async def list_indexes(
    client: QdrantClient = Depends(get_qdrant_client)
):
    collections = get_collections(client)
    return {"indexes": collections}