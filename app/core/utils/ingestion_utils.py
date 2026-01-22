from qdrant_client.http import models
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse

from app.core.settings import settings

def ensure_collection(
        client: QdrantClient, 
        collection_name: str
        ) -> dict:
    result = {"collection": collection_name, "collection_status": None}
    try:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=1536,
                distance=models.Distance.COSINE,
            ),
            hnsw_config=models.HnswConfigDiff(m=16, ef_construct=128),
        )
        result["collection_status"] = "created"
    except UnexpectedResponse as e:
        if e.status_code == 409:
            result["collection_status"] = "exists"
        else:
            raise
    return result

def delete_collection(
        client: QdrantClient,
        collection_name: str
        ) -> bool:
    return client.delete_collection(collection_name)
    
def get_collections(client: QdrantClient) -> list:
    """Return a list of current collection names in Qdrant."""
    return [col.name for col in client.get_collections().collections]

if __name__ == "__main__":
    qc = QdrantClient(url=settings.qdrant_url)
    print(ensure_collection(qc, "testing_2"))
    print(delete_collection(qc, "testing_2"))
    print(get_collections(qc))