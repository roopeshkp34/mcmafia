from fastapi import APIRouter
from app.api.server import document_extractor

router = APIRouter()

router.include_router(document_extractor.router, tags=["document-extractor"])
