import os
import httpx
import re
import asyncio
from llama_cloud import AsyncLlamaCloud
from app.db.database import DatabaseClient
from app.core.config import settings

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

    async def download_images(self, result):
        for image in result.images_content_metadata.images:
            if image.presigned_url is None or not self.is_page_screenshot(
                image.filename
            ):
                continue

            print(f"Downloading {image.filename}, {image.size_bytes} bytes")
            try:
                async with httpx.AsyncClient() as http_client:
                    response = await http_client.get(image.presigned_url)
                    with open(f"{image.filename}", "wb") as img_file:
                        img_file.write(response.content)
            except Exception as e:
                print(f"Error downloading image {image.filename}: {e}")

    async def parse_document(self, file: UploadFile):

        # Upload and parse a document
        file_obj = await self.client.files.create(
            file=file.file , purpose="parse"
        )

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
            "markdown_pages": [page.markdown for page in result.markdown.pages],
            "text_pages": [page.text for page in result.text.pages],
            "tables": [],
        }

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
        inserted_id = await self.db_client.insert_parsed_data("parsed_documents", parsed_data)
        print(f"Successfully pushed parsed data to MongoDB with ID: {inserted_id}")

        # Download screenshots
        await self.download_images(result)

        return inserted_id


async def main():
    parser = LlamaParser()
    # Default file from original script
    file_to_parse = "./attention_is_all_you_need.pdf"
    if os.path.exists(file_to_parse):
        await parser.parse_document(file_to_parse)
    else:
        print(f"File not found: {file_to_parse}")


if __name__ == "__main__":
    asyncio.run(main())
