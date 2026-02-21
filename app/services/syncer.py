import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.db.database import DatabaseClient
from app.db.elasticsearch_client import es_client
from app.services.embedding import embedding_service
from app.services.enrichment import enrichment_service
from app.core.config import settings

logger = logging.getLogger(__name__)

class MongoToESSyncer:
    def __init__(self):
        self.db_client = DatabaseClient()
        self.collection_name = "parsed_documents"
        self.index_name = "documents"

    async def process_document(self, doc):
        """
        Enriches and indexes a single MongoDB document into Elasticsearch.
        """
        file_name = doc.get("file_name", "UNKNOWN")
        pages = doc.get("json_pages", [])
        
        # Extract text from first page for company identification
        first_page_text = ""
        if pages:
            page = pages[0]
            if isinstance(page, dict):
                first_page_text = page.get("text", "")
                if not first_page_text and "items" in page:
                     # Flatten items recursively or just take first level
                     first_page_text = self._flatten_text(page.get("items", []))

        # Advanced Enrichment
        company_name = await enrichment_service.identify_company(first_page_text or file_name)
        ticker = await enrichment_service.identify_ticker(first_page_text or file_name)
        enrichment_data = await enrichment_service.fetch_tavily_enrichment(company_name)
        
        logger.info(f"Syncing document: {file_name} (Company: {company_name}, Ticker: {ticker})")
        
        for i, page in enumerate(pages):
            text_content = ""
            page_items = []
            if isinstance(page, dict):
                text_content = page.get("text", "")
                items = page.get("items", [])
                if not text_content and items:
                    text_content = self._flatten_text(items)
                
                # Extract items with bboxes
                page_items = self._extract_es_items(items)
            
            if not text_content:
                continue
                
            # Get embedding
            vector = await embedding_service.get_embedding(text_content)
            
            # Enrich metadata
            metadata = {
                "company_ticker": ticker,
                "company_name": company_name,
                "page_number": i + 1,
                "file_name": file_name,
                **enrichment_data # Add Tavily info
            }
            metadata = enrichment_service.enrich_page(text_content, metadata)
            
            es_doc = {
                "text": text_content,
                "vector_embedding": vector,
                "metadata": metadata,
                "items": page_items,
                "filing_date": "2024-01-01" 
            }
            
            # Index into ES
            try:
                await es_client.index_document(self.index_name, es_doc, doc_id=f"{doc['_id']}_p{i+1}")
            except Exception as e:
                logger.error(f"Error indexing page {i+1} of {file_name}: {e}")
            
        logger.info(f"Finished syncing {len(pages)} pages for {file_name}")

    def _flatten_text(self, items):
        text_parts = []
        for item in items:
            if isinstance(item, dict):
                val = item.get("value") or item.get("text") or item.get("md", "")
                if val:
                    text_parts.append(str(val))
                if "items" in item:
                    text_parts.append(self._flatten_text(item["items"]))
        return "\n".join(text_parts)

    def _extract_es_items(self, items):
        es_items = []
        for item in items:
            if isinstance(item, dict):
                text = item.get("value") or item.get("text") or item.get("md", "")
                bbox = item.get("bbox", [])
                if text and bbox:
                    es_items.append({
                        "text": str(text),
                        "bbox": bbox
                    })
                if "items" in item:
                    es_items.extend(self._extract_es_items(item["items"]))
        return es_items

    async def sync_existing_data(self):
        """
        One-time sync for existing MongoDB data.
        """
        logger.info("Starting initial sync of existing data...")
        try:
            cursor = self.db_client.db[self.collection_name].find()
            async for doc in cursor:
                await self.process_document(doc)
            logger.info("Initial sync completed.")
        except Exception as e:
            logger.error(f"Error during initial sync: {e}")

    async def start_watching(self):
        """
        Starts the MongoDB Change Stream listener.
        """
        logger.info(f"Starting Change Stream listener on {self.collection_name}...")
        try:
            async with self.db_client.db[self.collection_name].watch(full_document="updateLookup") as stream:
                async for change in stream:
                    if change["operationType"] in ["insert", "replace"]:
                        doc = change["fullDocument"]
                        logger.info(f"Detected {change['operationType']} in Mongo: {doc.get('file_name')}")
                        await self.process_document(doc)
        except Exception as e:
            logger.error(f"Error in Change Stream listener: {e}")
            await asyncio.sleep(5)  # Backoff
            await self.start_watching() # Restart

    async def run(self):
        """
        Main entry point for the syncer.
        """
        # Ensure index exists
        from app.parser.lama_parser import ES_MAPPING
        logger.info(f"Ensuring Elasticsearch index '{self.index_name}' exists...")
        await es_client.create_index(self.index_name, ES_MAPPING)
        
        # Small wait for ES to be ready
        await asyncio.sleep(1)
        
        # Run initial sync
        await self.sync_existing_data()
        
        # Start continuous watching
        await self.start_watching()

syncer = MongoToESSyncer()
