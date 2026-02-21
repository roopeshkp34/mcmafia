from typing import Optional
from fastapi import APIRouter
from app.models.chat import ChatRequest, ChatResponse
from app.services.chat import chat_service

from app import crud

router = APIRouter()


@router.post("/chat", response_model=Optional[ChatResponse])
async def chat(request: ChatRequest):
    """
    Endpoint to interact with the hierarchical agent system.
    """
    chat = await crud.chat.get_chat(request.thread_id)
    if chat:
        new_chat = {"type": "user", "content": request.query}
        chat["messages"].append(new_chat)
        await crud.chat.update_chat(request.thread_id, chat)
    else:
        db_obj = {
            "thread_id": request.thread_id,
            "title": await chat_service.generate_title(request.query),
            "messages": [{"type": "user", "content": request.query}],
        }
        chat = await crud.chat.create_chat(db_obj)
    result = await chat_service.chat(request.query)

    new_chat = {"type": "assistant", "content": result["response"], "metadata": result}
    chat["messages"].append(new_chat)
    await crud.chat.update_chat(request.thread_id, chat)
    # return ChatResponse(
    #     response=result["response"],
    #     agent_steps=result.get("agent_steps"),
    #     reasoning_for_response=result.get("reasoning_for_response")
    # )
    return result


@router.get("/chat/{thread_id}")
async def get_chat(thread_id: str):
    chat = await crud.chat.get_chat(thread_id)
    if chat:
        chat["_id"] = str(chat["_id"])
    return chat


@router.get("/chats")
async def get_chats():
    chats = await crud.chat.get_chats()
    return chats
