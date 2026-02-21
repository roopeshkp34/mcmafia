from typing import Optional
from fastapi import APIRouter
from app.models.chat import ChatRequest, ChatResponse
from app.services.chat import chat_service

router = APIRouter()


@router.post("/chat", response_model=Optional[ChatResponse])
async def chat(request: ChatRequest):
    """
    Endpoint to interact with the hierarchical agent system.
    """
    result = await chat_service.chat(request.query)
    
    # return ChatResponse(
    #     response=result["response"],
    #     agent_steps=result.get("agent_steps"),
    #     reasoning_for_response=result.get("reasoning_for_response")
    # )
    return result
