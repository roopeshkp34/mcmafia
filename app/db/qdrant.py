from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

from app.core.config import settings


class QdrantDB:
    _instance: Optional["QdrantDB"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QdrantDB, cls).__new__(cls)
            cls._instance.client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
            )
        return cls._instance

    def create_collection(
        self,
        collection_name: str,
        size: int = 1536,
        distance: Distance = Distance.COSINE,
    ):
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=size, distance=distance),
        )

    def save(
        self,
        collection_name: str,
        points: List[PointStruct],
    ):
        """Save vectors to a collection."""
        return self.client.upsert(
            collection_name=collection_name,
            points=points,
        )


qdrant_db = QdrantDB()
