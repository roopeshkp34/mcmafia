import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

class DatabaseClient:
    def __init__(self):
        self.mongo_url = os.getenv("mongo_url")
        self.db_name = os.getenv("mongo_db_name", "mcmafia")
        
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

    async def close(self):
        self.client.close()
