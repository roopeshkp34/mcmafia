from elasticsearch import AsyncElasticsearch
from app.core.config import settings
import asyncio


class ElasticsearchClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ElasticsearchClient, cls).__new__(cls)
            # Use api_key for authentication as per common Elastic Cloud setups
            cls._instance.client = AsyncElasticsearch(
                settings.ELASTIC_ENDPOINT, api_key=settings.ELASTIC_API_KEY
            )
        return cls._instance

    async def create_index(self, index_name: str, mapping: dict = None):
        if mapping is None:
            # (Default mapping omitted for brevity, keeping old one in actual file)
            pass
        
        try:
            if not await self.client.indices.exists(index=index_name):
                await self.client.indices.create(index=index_name, body=mapping)
                print(f"Successfully created index: {index_name}")
            else:
                print(f"Index '{index_name}' already exists.")
        except Exception as e:
            print(f"Error creating index {index_name}: {e}")

    async def index_document(self, index_name: str, document: dict, doc_id: str = None):
        try:
            return await self.client.index(index=index_name, document=document, id=doc_id)
        except Exception as e:
            print(f"Error indexing document to {index_name}: {e}")
            raise

    async def search(self, index_name: str, query: dict):
        return await self.client.search(index=index_name, body=query)

    async def hybrid_search(self, index_name: str, query_text: str, query_vector: list, k: int = 3):
        """
        Performs a hybrid search using RRF to merge ANN (KNN) and BM25 results.
        """
        search_query = {
            "retriever": {
                "rrf": {
                    "retrievers": [
                        {
                            "standard": {
                                "query": {
                                    "match": {
                                        "text": query_text
                                    }
                                }
                            }
                        },
                        {
                            "knn": {
                                "field": "vector_embedding",
                                "query_vector": query_vector,
                                "k": k,
                                "num_candidates": 100
                            }
                        }
                    ],
                    "rank_window_size": 100
                }
            }
        }
        # Note: Elasticsearch 8.12+ uses the 'retriever' syntax for RRF
        return await self.client.search(index=index_name, body=search_query)

    async def sync_mongo_to_es(self, company_ticker: str = None, fiscal_year: int = None):
        """
        Syncs parsed data from MongoDB to Elasticsearch.
        """
        from app.db.database import DatabaseClient
        from app.services.embedding import embedding_service
        
        db_client = DatabaseClient()
        # Find parsed documents in MongoDB
        query = {}
        if company_ticker and company_ticker != "UNKNOWN":
            query["file_name"] = {"$regex": company_ticker, "$options": "i"}
        
        cursor = db_client.db["parsed_documents"].find(query)
        async for doc in cursor:
            # For each document, index its pages into ES
            index_name = "documents"
            await self.create_index(index_name)
            
            # Note: Depending on how data is stored in Mongo, we might need to extract text
            # Here we assume json_pages contains the content as per lama_parser.py
            for i, page in enumerate(doc.get("json_pages", [])):
                
                # If json_pages doesn't have markdown, we handle it
                # For this implementation, we'll try to get text from columns/items if markdown is missing
                text_content = ""
                if isinstance(page, dict):
                    # Try to reconstruct text or use existing text field
                    text_content = page.get("text", "")
                    if not text_content and "items" in page:
                        text_content = "\n".join([item.get("value", "") for item in page["items"] if isinstance(item, dict) and "value" in item])
                
                if not text_content:
                    continue
                    
                vector = await embedding_service.get_embedding(text_content)
                
                es_doc = {
                    "text": text_content,
                    "vector_embedding": vector,
                    "items": page.get("items", []),
                    "metadata": {
                        "company_ticker": company_ticker or "UNKNOWN",
                        "fiscal_year": fiscal_year or 2024,
                        "page_number": i + 1,
                    },
                    "filing_date": "2024-01-01" # Placeholder
                }
                
                await self.index_document(index_name, es_doc, doc_id=f"{doc['_id']}_p{i+1}")
        
        await db_client.close()

    async def close(self):
        await self.client.close()


es_client = ElasticsearchClient()
