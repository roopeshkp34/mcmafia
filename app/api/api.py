from fastapi import APIRouter
from app.api.server import document_extractor, chat

router = APIRouter()

router.include_router(document_extractor.router, tags=["document-extractor"])
router.include_router(chat.router, tags=["chat"])
