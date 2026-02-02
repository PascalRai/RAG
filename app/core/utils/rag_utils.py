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
"""You are an AI assistant with access to a financial report retrieval tool.

1. If the query is NOT about financial reports, answer directly using your knowledge. Do NOT call any tools.

2. If the query IS about financial reports:
   a. If SIMPLE (single-hop), perform EXACTLY ONE retrieval and answer using ONLY retrieved context.
   b. If COMPLEX (multi-hop), decompose into 2–3 distinct, non-overlapping sub-questions. For each:
      - Perform EXACTLY ONE retrieval specific to that sub-question.
      - Do NOT reuse or paraphrase previous retrievals.
   After all retrievals, synthesize a single detailed answer, grounded only in retrieved context.

3. If context lacks relevant information, respond: "Insufficient relevant financial data found." Do NOT infer or mix companies unless requested.

4. Do NOT mention tool calls or sub-questions in your final answer; write a coherent, analytical response.
"""
)

memory = InMemorySaver()

def get_rag_agent():
    """Returns a configured RAG agent instance."""
    return create_agent(
        model,
        tools,
        system_prompt=prompt,
        checkpointer=memory
    )