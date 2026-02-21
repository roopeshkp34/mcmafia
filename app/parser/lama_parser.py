import os
import httpx
import re
import asyncio
from llama_cloud import AsyncLlamaCloud
from fastapi import UploadFile

from app.db.database import DatabaseClient
from app.core.config import settings
from app.db.elasticsearch_client import es_client
from app.services.embedding import embedding_service

ES_MAPPING = {
    "mappings": {
        "properties": {
            "text": {"type": "text"},
            "vector_embedding": {
                "type": "dense_vector",
                "dims": 1536,
                "index": True,
                "similarity": "cosine",
            },
            "metadata": {
                "properties": {
                    "company_ticker": {"type": "keyword"},
                    "fiscal_year": {"type": "integer"},
                    "report_type": {"type": "keyword"},
                    "section_name": {"type": "keyword"},
                    "page_number": {"type": "integer"},
                    "chunk_index": {"type": "integer"},
                    "total_chunks": {"type": "integer"},
                }
            },
            "filing_date": {"type": "date"},
        }
    }
}

# In LlamaCloud SDK some types might be needed for isinstance checks if they are exported
# If not, we can use Duck Typing or internal imports
try:
    from llama_cloud.types import ItemsPageStructuredResultPageItemTableItem
except ImportError:
    ItemsPageStructuredResultPageItemTableItem = type(None)  # Fallback


class LlamaParser:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.LLAMA_PARSE_API_KEY
        if not self.api_key:
            raise ValueError("llama_parse_key not found in environment variables")

        self.client = AsyncLlamaCloud(api_key=self.api_key)
        self.db_client = DatabaseClient()

    def is_page_screenshot(self, image_name: str) -> bool:
        return re.match(r"^page_(\d+)\.jpg$", image_name) is not None

    # async def download_images(self, result):
    #     for image in result.images_content_metadata.images:
    #         if image.presigned_url is None or not self.is_page_screenshot(
    #             image.filename
    #         ):
    #             continue

    #         print(f"Downloading {image.filename}, {image.size_bytes} bytes")
    #         try:
    #             async with httpx.AsyncClient() as http_client:
    #                 response = await http_client.get(image.presigned_url)
    #                 with open(f"{image.filename}", "wb") as img_file:
    #                     img_file.write(response.content)
    #         except Exception as e:
    #             print(f"Error downloading image {image.filename}: {e}")

    async def parse_document(self, file: UploadFile):

        # Upload and parse a document
        file_obj = await self.client.files.create(file=file.file, purpose="parse")

        result = await self.client.parsing.parse(
            file_id=file_obj.id,
            tier="agentic",
            version="latest",
            input_options={},
            output_options={
                "markdown": {
                    "tables": {
                        "output_tables_as_markdown": False,
                    },
                },
                "images_to_save": ["screenshot"],
            },
            processing_options={
                "ignore": {
                    "ignore_diagonal_text": True,
                },
                "ocr_parameters": {"languages": ["fr"]},
            },
            expand=["text", "markdown", "items", "images_content_metadata"],
        )

        # Prepare data for MongoDB
        parsed_data = {
            "file_id": file_obj.id,
            "file_name": file.filename,
            "json_pages": [
                page.model_dump() if hasattr(page, "model_dump") else page
                for page in result.items.pages
            ],
            "tables": [],
        }
        print(result)

        # Extract tables
        for page in result.items.pages:
            for item in page.items:
                if hasattr(item, "rows") and hasattr(
                    item, "b_box"
                ):  # Generic check if class import failed
                    parsed_data["tables"].append(
                        {
                            "page_number": page.page_number,
                            "rows": item.rows,
                            "b_box": item.b_box,
                        }
                    )

        # Insert into MongoDB
        inserted_id = await self.db_client.insert_parsed_data(
            "parsed_documents", parsed_data
        )
        print(f"Successfully pushed parsed data to MongoDB with ID: {inserted_id}")

        # Index into Elasticsearch for Semantic Search
        # Using a fixed index name for now as in previous implementation
        index_name = "documents"
        await es_client.create_index(index_name, ES_MAPPING)

        total_pages = len(result.markdown.pages)
        for i, page in enumerate(result.markdown.pages):
            print(f"Vectorizing and indexing page {i+1}/{total_pages}...")

            # Generate embedding for the markdown content
            vector = await embedding_service.get_embedding(page.markdown)

            # Prepare metadata (placeholders or extracted)
            metadata = {
                "company_ticker": "UNKNOWN",  # Placeholder
                "fiscal_year": 2024,  # Placeholder
                "report_type": "10-K",  # Placeholder
                "section_name": "General",  # Placeholder
                "page_number": i + 1,
                "chunk_index": 0,  # Assuming 1 chunk per page for now
                "total_chunks": 1,
            }

            es_doc = {
                "text": page.markdown,
                "vector_embedding": vector,
                "metadata": metadata,
                "filing_date": "2024-01-01",  # Placeholder
            }

            await es_client.index_document(
                index_name, es_doc, doc_id=f"{file_obj.id}_p{i+1}"
            )

        # Download screenshots
        # await self.download_images(result)

        return inserted_id
