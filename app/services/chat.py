from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
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
        bboxes = []
        original_text = []
        source = hit.get("_source", {})
        metadata = source.get("metadata", {})
        file_name =metadata.get("file_name")
        
        # Collect bounding boxes from both metadata and items
        if "items" in source:
            for item in source["items"]:
                if isinstance(item, dict) and "bbox" in item:
                    bboxes.append(item["bbox"])
                if isinstance(item, dict) and "text" in item:
                    original_text.append(item["text"])
        
        
        results.append({
            "original_text": original_text,
            "metadata": metadata,
            "bounding_box": bboxes,
            "page_no": metadata.get("page_number"),
            "pdf_name": file_name,
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
        metadata = source.get("metadata", {})
        bboxes = []
        
        # Collect bounding boxes from both metadata and items
        if "items" in source:
            for item in source["items"]:
                if isinstance(item, dict) and "bbox" in item:
                    bboxes.append(item["bbox"])
        
        results.append({
            "text": source.get("text"),
            "metadata": metadata,
            "bounding_box": bboxes,
            "page_no": metadata.get("page_number"),
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
class SourceDocumentInfo(BaseModel):
    page_no: int = Field(description="Page number of the source document")
    bounding_box: List[float] = Field(description="Bounding box coordinates [x0, y0, x1, y1] for the source text. If a page has multiple relevant boxes, provide them as separate source entries. bbox in the tool output is a list of floats")

class SupervisorResponse(BaseModel):
    reasoning_for_response: str = Field(description="Detailed reasoning for the final answer, explaining the logic and steps used. Use the sources to justify your reasoning.")
    answer: str = Field(description="The final direct answer to the user's query.")
    sources: List[SourceDocumentInfo] = Field(description="List of source documents with page numbers and bounding boxes retrieved from tool outputs. These are in the response of tool calls")

supervisor = create_supervisor(
    agents=[data_extraction_agent, rag_agent, forensic_critic_agent],
    model=llm,
    prompt=(
        """
        You are a forensic financial supervisor. You coordinate a team of agents to identify 'Narrative Divergence' in financial filings."
        "\n\nWorkflow:"
        "\n1. When asked about inventory bloat or financial trends, first involve the data_extraction_agent to pull metrics and check for triggers."
        "\n2. If a trigger is hit (Inventory growth > Sales + 15%), hand over to the forensic_critic_agent for an ANN-driven narrative audit."
        "\n3. Use the rag_agent for general document queries."
        "\n\nYou MUST provide a structured response containing your reasoning, the final answer, and all relevant sources."
        "\n\nCRITICAL RULES:"
        "\n1. reasoning_for_response: This is for INTERNAL LOGIC. Explain WHICH agents were called, WHAT specific data they returned (e.g., specific numbers like 20%% inventory growth), and WHY you reached your conclusion. This should be a technical justification."
        "\n2. answer: This is for the USER. Provide a concise, clear, and direct response. DO NOT repeat the technical reasoning here unless it's necessary for the user's understanding."
        "\n3. sources: For each piece of information used in the answer, you MUST include a source entry with 'page_no' and 'bounding_box'."
        "\n4. bounding_box: MUST be a list of 4 floats: [x0, y0, x1, y1]. Extract these exactly from tool outputs. If multiple boxes are returned for a page, create separate SourceDocumentInfo entries for each."
        "\n\nExample of Good Reasoning:"
        "\n'I called the data_extraction_agent which found that Inventory increased by 22%% while Sales grew by only 4%%. Since the divergence is > 15%%, I then tasked the forensic_critic_agent to examine management justifications. The critic found that while management claimed supply chain optimism, footnotes indicated slow-moving clearance stock, confirming a high Narrative Divergence.'"
        "
        Your output format should be like the following
        
        {
            "reasoning_for_response": "<reasoning>",
            "response": "<answer>",
            "sources": [
                {
                    "page_no": <page_no>,
                    "original_text": "<original_text>",
                    "file_name": "<file_name>",
                    "bounding_box": [<bbox>]
                },
                {
                    "page_no": <page_no>,
                    "original_text": "<original_text>",
                    "file_name": "<file_name>",
                    "bounding_box": [<bbox>]
                }
    ]
    }

        """

    ),
    add_handoff_back_messages=True,
    output_mode="full_history",
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
        
        # Extract structured response if present
        structured_response = result.get("structured_response")
        
        # Extract the last message from the result
        messages = result.get("messages", [])
        
        # Collect steps and source documents with traceability
        steps = []
        source_documents = []
        
        # If we have a structured response, use it for primary values
        if structured_response:
            reasoning_for_response = structured_response.reasoning_for_response
            response_text = structured_response.answer
            
            # Group boxes by page_no
            page_to_boxes = {}
            for s in structured_response.sources:
                if s.page_no not in page_to_boxes:
                    page_to_boxes[s.page_no] = []
                # Ensure we add the box if it's not already there
                if s.bounding_box not in page_to_boxes[s.page_no]:
                    page_to_boxes[s.page_no].append(s.bounding_box)
            
            source_documents = [
                {"page_no": p, "bounding_box": boxes}
                for p, boxes in page_to_boxes.items()
            ]
        else:
            # Fallback logic for extraction if structured_response is missing
            last_message = messages[-1] if messages else None
            response_text = last_message.content if last_message and hasattr(last_message, "content") else "No response generated."
            
            # Try to find a supervisor message with reasoning
            reasoning_for_response = "Logic execution completed. Please check agent steps for details."
            for msg in reversed(messages):
                if getattr(msg, "name", None) == "supervisor" and hasattr(msg, "content") and msg.content:
                    reasoning_for_response = msg.content[:500]
                    break

        # Always collect source documents from tool messages as a robust fallback/supplement
        for msg in messages:
            agent_name = getattr(msg, "name", None) or "supervisor"
            
            # Extract tool calls and results
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    steps.append({
                        "agent": str(agent_name),
                        "tool": tc.get("name"),
                        "input": tc.get("args")
                    })
            
            # If it's a ToolMessage, try to extract bounding boxes
            if msg.type == "tool":
                try:
                    import json
                    import ast
                    # Tool outputs might be JSON or Python string representation
                    content_str = msg.content
                    try:
                        content_data = json.loads(content_str)
                    except:
                        # Fallback to ast.literal_eval for Python-style list strings
                        content_data = ast.literal_eval(content_str)
                        
                    if isinstance(content_data, list):
                        for item in content_data:
                            if isinstance(item, dict) and "bounding_box" in item:
                                raw_box = item.get("bounding_box", [])
                                # Normalize boxes: Handle various nested formats
                                normalized_boxes = []
                                def extract_box(b):
                                    if isinstance(b, dict):
                                        return [
                                            float(b.get('x', 0)), 
                                            float(b.get('y', 0)), 
                                            float(b.get('w', 0)), 
                                            float(b.get('h', 0))
                                        ]
                                    elif isinstance(b, list) and len(b) > 0:
                                        if isinstance(b[0], dict):
                                            return extract_box(b[0])
                                        return [float(coord) for coord in b]
                                    return None

                                if isinstance(raw_box, list):
                                    for b in raw_box:
                                        box = extract_box(b)
                                        if box:
                                            normalized_boxes.append(box)
                                else:
                                    box = extract_box(raw_box)
                                    if box:
                                        normalized_boxes = [box]

                                page_no = item.get("page_no")
                                if page_no is None:
                                    page_no = item.get("metadata", {}).get("page_number", 0)
                                
                                doc_info = {
                                    "page_no": page_no,
                                    "bounding_box": normalized_boxes
                                }
                                # Deduplicate based on page and boxes
                                if doc_info not in source_documents:
                                    source_documents.append(doc_info)
                except Exception as e:
                    # Silently fail for malformed tool messages
                    pass

            elif hasattr(msg, "content") and msg.content and agent_name != "supervisor" and agent_name:
                steps.append({
                    "agent": str(agent_name),
                    "content": msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
                })

        return {
            "response": response_text,
            "source_documents": source_documents,
            "agent_steps": steps,
            "reasoning_for_response": reasoning_for_response
        }


chat_service = ChatService()
