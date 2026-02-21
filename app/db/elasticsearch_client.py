from elasticsearch import AsyncElasticsearch
from app.core.config import settings


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

    async def create_index(self, index_name: str, mapping: dict):
        if not await self.client.indices.exists(index=index_name):
            await self.client.indices.create(index=index_name, body=mapping)
            print(f"Created index: {index_name}")

    async def index_document(self, index_name: str, document: dict, doc_id: str = None):
        return await self.client.index(index=index_name, document=document, id=doc_id)

    async def search(self, index_name: str, query: dict):
        return await self.client.search(index=index_name, body=query)

    async def close(self):
        await self.client.close()


es_client = ElasticsearchClient()
