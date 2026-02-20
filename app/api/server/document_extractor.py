from typing import List
from fastapi import APIRouter, UploadFile, File

router = APIRouter()


@router.post("/document-extractor")
async def document_extractor(files: List[UploadFile] = File(...)):
    return {"message": f"Received {len(files)} files"}
