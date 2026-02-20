from typing import List
from fastapi import APIRouter, UploadFile, File


from app.parser.lama_parser import LlamaParser
router = APIRouter()


@router.post("/document-extractor")
async def document_extractor(files: List[UploadFile] = File(...)):
    lama_parser = LlamaParser()

    for file in files:
        await lama_parser.parse_document(file)
    
    return {"message": f"Received {len(files)} files"}
