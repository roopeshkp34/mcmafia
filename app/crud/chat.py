from app.db.database import DatabaseClient


class ChatCRUD:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.db_client = DatabaseClient()
        self.collection = self.db_client.db[self.collection_name]

    async def get_chat(self, thread_id: str):
        # DatabaseClient.db is initialized in __init__
        return await self.collection.find_one({"thread_id": thread_id})

    async def create_chat(self, chat):
        await self.db_client.insert(self.collection, chat)
        return await self.get_chat(chat["thread_id"])

    async def update_chat(self, thread_id: str, chat):
        # DatabaseClient.update already handles the _id pop
        return await self.db_client.update(
            self.collection, {"thread_id": thread_id}, chat
        )


chat = ChatCRUD("chat")
