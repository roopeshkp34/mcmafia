import asyncio
import os
from app.db.database import DatabaseClient

async def test_mongodb_connection():
    print("Testing MongoDB connection...")
    try:
        db_client = DatabaseClient()
        test_data = {
            "test_key": "test_value",
            "description": "Integration test for DatabaseClient"
        }
        # Fixed: insert_parsed_data requires collection_name
        inserted_id = await db_client.insert_parsed_data("test_collection", test_data)
        print(f"Successfully inserted test data. ID: {inserted_id}")
        
        # Cleanup
        await db_client.collection.delete_one({"_id": inserted_id})
        print("Successfully cleaned up test data.")
        
        await db_client.close()
        print("MongoDB connection test passed!")
        return True
    except Exception as e:
        print(f"MongoDB connection test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_mongodb_connection())
