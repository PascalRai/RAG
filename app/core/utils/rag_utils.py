import os
from app.core.settings import settings
from langchain.agents import create_agent
from langchain_openai import OpenAIEmbeddings
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver

from app.core.utils.retirever_tool import retrieve_context

os.environ['OPENAI_API_KEY'] = settings.openai_api_key

model = init_chat_model(model=settings.llm_openai_model)
embeddings = OpenAIEmbeddings(model=settings.model_id)

tools = [retrieve_context]

prompt = (
    "You have access to a tool that retrieves context from a Financial Reports. "
    "Use the tool to help answer user queries."
)

def get_rag_agent():
    """Returns a configured RAG agent instance."""
    return create_agent(
        model,
        tools,
        system_prompt=prompt,
        checkpointer=InMemorySaver()
    )