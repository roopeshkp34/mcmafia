from openai import AsyncAzureOpenAI
from app.core.config import settings


class EmbeddingService:
    def __init__(self):
        self.client = AsyncAzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_version=settings.AZURE_OPENAI_API_VERSION,
        )
        self.deployment = settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT

    async def get_embedding(self, text: str):
        response = await self.client.embeddings.create(
            input=[text], model=self.deployment
        )
        return response.data[0].embedding


embedding_service = EmbeddingService()
