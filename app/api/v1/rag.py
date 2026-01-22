from fastapi import APIRouter, Depends, HTTPException, Query
from qdrant_client import QdrantClient
from langchain_core.runnables import RunnableConfig
from app.core.utils.retirever_tool import RetrievalContext
from app.core.utils.rag_utils import get_rag_agent
from fastapi.responses import StreamingResponse
from app.core.settings import settings

router = APIRouter()

def get_qdrant_client() -> QdrantClient:
    try:
        return QdrantClient(url=settings.qdrant_url)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not connect to Qdrant: {str(e)}")

@router.post("/rag")
async def rag_endpoint(
    query: str = Query(..., description="User input query"),
    collection_name: str = Query("test_01", description="Qdrant collection name"),
    thread_id: str = Query(None, description="Thread ID"),
    client: QdrantClient = Depends(get_qdrant_client)
):
    agent = get_rag_agent()
    config: RunnableConfig = {"configurable": {"thread_id": thread_id or "default_thread"}}
    context = RetrievalContext(client=client, collection_name=collection_name)
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": query}]},
        config=config,
        context=context
    )
    # Extract only the last AI response
    messages = result.get("messages", [])
    last_message = messages[-1] if messages else None
    response_content = last_message.content if last_message and hasattr(last_message, 'content') else ""
    return {"response": response_content}


@router.post("/rag/stream")
async def rag_stream_endpoint(
    query: str = Query(..., description="User input query"),
    collection_name: str = Query("test_01", description="Qdrant collection name"),
    thread_id: str = Query(None, description="Thread ID"),
    client: QdrantClient = Depends(get_qdrant_client)
):
    agent = get_rag_agent()
    config: RunnableConfig = {"configurable": {"thread_id": thread_id or "default_thread"}}
    context = RetrievalContext(client=client, collection_name=collection_name)

    async def event_generator():
        async for chunk in agent.astream(
            {"messages": [{"role": "user", "content": query}]},
            config=config,
            context=context,
            stream_mode="messages"
        ):
            yield f"data: {chunk[0]}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")