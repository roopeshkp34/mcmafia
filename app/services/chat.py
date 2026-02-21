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
async def _query_documents_logic(query: str) -> List[Dict[str, Any]]:
    """Helper function for querying documents."""
    vector = await embedding_service.get_embedding(query)
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


@tool
async def query_documents(query: str) -> List[Dict[str, Any]]:
    """
    Query the elastic search database to retrieve relevant document chunks for a given user query.
    Returns a list of matching document snippets and their metadata.
    """
    return await _query_documents_logic(query)


@tool
async def extract_financial_metrics(company_ticker: str) -> Dict[str, Any]:
    """
    Extracts Revenue and Inventory metrics for 2024 and 2025 for a given company.
    Used to identify if there is an 'Inventory Bloat' trigger.
    """
    # Search for Revenue and Inventory in the documents
    query = f"Total Revenue and Total Inventory for {company_ticker} in 2024 and 2025"
    results = await _query_documents_logic(query)
    
    return {"company": company_ticker, "data": results}


@tool
async def ann_narrative_search(query: str) -> List[Dict[str, Any]]:
    """
    Performs an HNSW-based ANN search for management explanations.
    Uses RRF to merge with BM25 results for terms like 'obsolescence' or 'write-down'.
    """
    vector = await embedding_service.get_embedding(query)
    index_name = "documents"
    
    # Use the hybrid search with RRF that we added to es_client
    response = await es_client.hybrid_search(index_name, query, vector, k=3)
    
    results = []
    for hit in response.get("hits", {}).get("hits", []):
        source = hit.get("_source", {})
        results.append({
            "text": source.get("text"),
            "metadata": source.get("metadata"),
            "score": hit.get("_score")
        })
    
    return results


# 3. Create Agents

# Data Extraction Agent
data_extraction_agent = create_react_agent(
    model=llm,
    tools=[extract_financial_metrics],
    name="data_extraction_agent",
    prompt=(
        "You are a financial data extractor. Your task is to pull 'Total Revenue' and 'Total Inventory' "
        "for 2024 and 2025 filings for a given company. "
        "If the percentage increase in Inventory is significantly higher (15%+) than the percentage increase in Sales (Revenue), "
        "flag this for an ANN-driven narrative audit by the forensic_critic_agent."
    )
)

# RAG Agent
rag_agent = create_react_agent(
    model=llm,
    tools=[query_documents],
    name="rag_agent",
    prompt="You are a retrieval-augmented generation assistant. Use the query_documents tool to find information."
)

# Forensic Critic Agent
forensic_critic_agent = create_react_agent(
    model=llm,
    tools=[ann_narrative_search],
    name="forensic_critic_agent",
    prompt=(
        "You are a Forensic Critic. When the inventory bloat trigger is hit, your task is to: "
        "1. Use the ann_narrative_search tool to find management's top 3 justifications for this buildup. "
        "2. Look for 'Strategic pre-buying' vs. 'Deteriorating demand.' "
        "3. Check if the ANN results surface terms like 'seasonal' in a non-seasonal quarter. "
        "4. The Critique: If management claims 'robust demand' but the ANN also surfaces footnotes about 'slow-moving stock,' "
        "flag a high Narrative Divergence score."
    )
)


# 4. Create Supervisor Agent
supervisor = create_supervisor(
    agents=[data_extraction_agent, rag_agent, forensic_critic_agent],
    model=llm,
    prompt=(
        "You are a forensic financial supervisor. You coordinate a team of agents to identify 'Narrative Divergence' in financial filings."
        "\n\nWorkflow:"
        "\n1. When asked about inventory bloat or financial trends, first involve the data_extraction_agent to pull metrics and check for triggers."
        "\n2. If a trigger is hit (Inventory growth > Sales + 15%), hand over to the forensic_critic_agent for an ANN-driven narrative audit."
        "\n3. Use the rag_agent for general document queries."
        "\n\nAlways return your final answer in a clear and professional manner with full traceability of the steps and logic."
        "Include the reasoning for your response and cite source documents."
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
        messages = result.get("messages", [])
        last_message = messages[-1]
        
        # Collect steps with traceability
        steps = []
        for msg in messages:
            agent_name = getattr(msg, "name", None) or "supervisor"
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    steps.append({
                        "agent": str(agent_name),
                        "tool": tc.get("name"),
                        "input": tc.get("args")
                    })
            elif hasattr(msg, "content") and msg.content and agent_name != "supervisor":
                steps.append({
                    "agent": str(agent_name),
                    "content": msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
                })

        # Reasoning from the last message or supervisor
        reasoning = getattr(last_message, "reasoning_for_response", "Logic execution completed successfully.")

        return {
            "response": last_message.content if hasattr(last_message, "content") else str(last_message),
            "agent_steps": steps,
            "reasoning_for_response": reasoning
        }


chat_service = ChatService()
