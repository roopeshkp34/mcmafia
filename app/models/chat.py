from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ChatRequest(BaseModel):
    query: str = Field(..., description="The user query to be processed by the agents")


class SourceDocument(BaseModel):
    page_no: int
    bounding_box: List[Dict[str, Any]]

class AgentStep(BaseModel):
    agent: str
    tool_calls: List[Dict[str, Any]]
    
class ChatResponse(BaseModel):
    response: str = Field(..., description="The assistant's response")
    source_documents: Optional[List[SourceDocument]] = Field(
        None, description="Source documents retrieved by the RAG agent"
    )
    agent_steps: Optional[List[AgentStep]] = Field(
        None, description="Internal steps taken by the agents"
    )
    reasoning_for_response: str = Field(..., description="Reasoning for the response")
