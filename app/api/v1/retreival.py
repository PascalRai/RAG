from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
from fastapi import APIRouter, Depends, HTTPException

from app.core.settings import settings
from app.core.utils.retriever_utils import dense_retrieve
from app.schemas.retreival_schema import RetreivalRequest, RetrievalResponse

router = APIRouter()

def get_qdrant_client() -> QdrantClient:
    try:
        return QdrantClient(url=settings.qdrant_url)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not connect to Qdrant: {str(e)}")

@router.post("/retrieve", response_model=RetrievalResponse)
async def retrieve(
    request: RetreivalRequest,
    client: QdrantClient = Depends(get_qdrant_client),
):
    response = await dense_retrieve(
        client,
        collection_name=request.index_name,
        query=request.query,
        top_k=request.top_k
    )

    results = [
        {
            "id": point.id,
            "score": float(point.score),
            "metadata": point.payload.get("metadata"),
            "text": point.payload.get("text"),
        }
        for point in response.points
    ]

    return {"results": results}
