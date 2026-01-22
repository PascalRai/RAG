import asyncio
from typing import Union, List
from dataclasses import dataclass
from qdrant_client import QdrantClient
from langchain.tools import tool, ToolRuntime

from app.core.utils.retriever_utils import dense_retrieve

@dataclass
class RetrievalContext:
    client: QdrantClient
    collection_name: str

@tool
def retrieve_context(
    query: Union[str, List[str]], 
    runtime: ToolRuntime[RetrievalContext]
):
    """
    Retrieve information to help answer a query.
    `query` can be a single query (str) or a list of sub-queries (List[str]).
    If a list is provided, retrievals will be run in parallel and results returned as a list.
    """
    collection_name = runtime.context.collection_name
    client = runtime.context.client

    async def single_retrieve(q):
        response = await dense_retrieve(
            client=client, 
            query=q, 
            collection_name=collection_name
        )
        points = response.model_dump()["points"]
        return "\n\n".join(
            f"Source: {ret_['payload']['metadata']}\nContent: {ret_['payload']['text']}"
            for ret_ in points
        )

    async def runner():
        if isinstance(query, list):
            return await asyncio.gather(*(single_retrieve(q) for q in query))
        else:
            return await single_retrieve(query)

    # ---- Sync wrapper around async code ----
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # Running inside an event loop (e.g. FastAPI, Jupyter, LangGraph async)
        return asyncio.run_coroutine_threadsafe(runner(), loop).result()
    else:
        # Normal sync environment
        return asyncio.run(runner())