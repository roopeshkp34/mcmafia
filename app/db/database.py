from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings


class DatabaseClient:
    def __init__(self):
        self.mongo_url = settings.MONGO_URI
        self.db_name = settings.MONGO_DB_NAME

        if not self.mongo_url:
            raise ValueError("mongo_url not found in environment variables")

        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]

    async def insert_parsed_data(self, collection_name: str, data: dict):
        """
        Inserts parsed document data into the MongoDB collection.
        """
        try:
            collection = self.db[collection_name]
            result = await collection.insert_one(data)
            return result.inserted_id
        except Exception as e:
            print(f"Error inserting data into MongoDB: {e}")
            raise

    async def insert(self, collection, data: dict):
        return await collection.insert_one(data)

    async def update(self, collection, query: dict, data: dict):
        """
        Updates data in the MongoDB collection.
        """
        try:
            # Avoid modifying _id field which is immutable in MongoDB
            update_data = data.copy()
            update_data.pop("_id", None)

            result = await collection.update_one(query, {"$set": update_data})
            return result.modified_count
        except Exception as e:
            print(f"Error updating data in MongoDB: {e}")
            raise

    async def close(self):
        self.client.close()
