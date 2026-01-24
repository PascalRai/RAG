from typing import Dict, Any
from qdrant_client import QdrantClient, models
from langchain_openai import OpenAIEmbeddings
from app.core.settings import settings

embeddings = OpenAIEmbeddings(
    model=settings.model_id,
    api_key=settings.openai_api_key
)

async def hydrid_retiever(
        client: QdrantClient,
        query: Any,
        collection_name: str,
        top_k: int = 3,
    ) -> Dict:
    """
    Query the Qdrant collection for the top_k most similar points to the query_embedding.
    
    Args:
        client (QdrantClient): The Qdrant client instance.
        collection_name (str): The name of the collection to query.
        query_embedding (Any): The embedding to use as a query.
        top_k (int): The number of top results to return.

    Returns:
        Dict: The query response from Qdrant.
    """
    query_embedding = await embeddings.aembed_query(query)
    return client.query_points(
        collection_name=collection_name,
        prefetch=[
            models.Prefetch(
                query=query_embedding,
                using="dense",
                limit=int(top_k*2.5),
            ),
            models.Prefetch(
                query=models.Document(
                    text=query,
                    model="Qdrant/bm25"
                ),
                using="bm25",
                limit=int(top_k*2.5),
            )
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        limit=top_k
    )