from typing import List, Dict, Any, Optional
from langchain_openai import AzureChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor

from app.core.config import settings
from app.db.elasticsearch_client import es_client
from app.services.embedding import embedding_service


# 1. Initialize LLM
llm = AzureChatOpenAI(
    azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT,
    api_key=settings.AZURE_OPENAI_API_KEY,
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_version=settings.AZURE_OPENAI_API_VERSION,
    temperature=0,
)


# 2. Define Tools
@tool
async def query_documents(query: str) -> List[Dict[str, Any]]:
    """
    Query the elastic search database to retrieve relevant document chunks for a given user query.
    Returns a list of matching document snippets and their metadata.
    """
    # Embed the query
    breakpoint()
    vector = await embedding_service.get_embedding(query)

    # Search Elasticsearch
    # Fixed index name as used in lama_parser.py
    index_name = "documents"
    
    es_query = {
        "knn": {
            "field": "vector_embedding",
            "query_vector": vector,
            "k": 5,
            "num_candidates": 50
        }
    }

    response = await es_client.search(index_name, es_query)
    
    results = []
    for hit in response.get("hits", {}).get("hits", []):
        source = hit.get("_source", {})
        results.append({
            "text": source.get("text"),
            "metadata": source.get("metadata"),
            "score": hit.get("_score")
        })
    
    return results


# 3. Create RAG Agent (ReAct)
rag_agent = create_react_agent(
    model=llm,
    tools=[query_documents],
    name="rag_agent",
    prompt="You are a retrieval-augmented generation assistant. Use the query_documents tool to find information."
)


# 4. Create Supervisor Agent
supervisor = create_supervisor(
    agents=[rag_agent],
    model=llm,
    prompt=(
        "You are a forensic financial supervisor. You have access to a rag_agent that can query financial documents."
        "Coordinate with the rag_agent to answer user questions about financial filings. "
        "Always return your final answer in a clear and professional manner. "
        "Also return the reasoning for your response."
        "Make sure to include the source documents in the response. And always give reasoning for your response."
    ),
    add_handoff_back_to_supervisor=True,
)


class ChatService:
    def __init__(self):
        self.app = supervisor.compile()

    async def chat(self, user_query: str) -> Dict[str, Any]:
        """
        Processes a user query through the hierarchical agent structure.
        """
        inputs = {"messages": [("user", user_query)]}
        
        # Invoke the compiled graph
        result = await self.app.ainvoke(inputs)
        
        # Extract the last message from the result
        last_message = result.get("messages", [])[-1]
        
        # Collect steps if needed (optional)
        steps = []
        for msg in result.get("messages", []):
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                steps.append({"agent": "rag_agent", "tool_calls": msg.tool_calls})

        return {
            "response": last_message.content if hasattr(last_message, "content") else str(last_message),
            "agent_steps": steps,
            "reasoning_for_response": last_message.reasoning_for_response
        }


chat_service = ChatService()
