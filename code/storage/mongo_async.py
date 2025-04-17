from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime
import asyncio

class MongoDB:
    def __init__(self, username, password, host, port):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        
        self.client = AsyncIOMotorClient(
            f"mongodb://{username}:{password}@{host}:{port}")
        
        self.db = self.client["Cook4You"]
        self.users = self.db["users"]
        self.chats = self.db["chats"]
        
    # Нужен индекс для поиска чатов пользователя
    async def create_indexes(self):
        await self.chats.create_index("user_id")

    # Создание нового пользователя
    async def create_user(self, email: str, password_hash: str) -> str:
        user = {
            "email": email,
            "password_hash": password_hash,
            "created_at": datetime.now()
        }
        result = await self.users.insert_one(user)
        return str(result.inserted_id)

    # Создание нового чата
    async def create_chat(self, user_id: str, title: str) -> str:
        chat = {
            "user_id": ObjectId(user_id),
            "title": title,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "messages": []
        }
        result = await self.chats.insert_one(chat)
        return str(result.inserted_id)

    # Добавление сообщения в чат
    async def add_message(self, chat_id: str, sender: str, type: str, content: str) -> bool:
        message = {
            "sender": sender,
            "type": type,  # "text" или "image"
            "content": content, # "text" или "url"
            "created_at": datetime.now()
        }
        result = await self.chats.update_one(
            {"_id": ObjectId(chat_id)},
            {
                "$push": {"messages": message},
                "$set": {"updated_at": datetime.now()}
            }
        )
        return result.modified_count > 0

    # Получение всех чатов пользователя
    async def get_chats_for_user(self, user_id: str):
        cursor = self.chats.find({"user_id": ObjectId(user_id)}, {"messages": 0, "user_id": 0})  # Без сообщений и user_id
        return [chat async for chat in cursor]

    # Получение сообщений конкретного чата
    async def get_chat_messages(self, chat_id: str):
        chat = await self.chats.find_one({"_id": ObjectId(chat_id)}, {"messages": 1})
        return chat["messages"] if chat else []

    # Удаление чата пользователя
    async def delete_chat_for_user(self, chat_id: str, user_id: str) -> bool:
        result = await self.chats.delete_one({
            "_id": ObjectId(chat_id),
            "user_id": ObjectId(user_id)
        })
        return result.deleted_count == 1

    # Удаление всех чатов пользователя
    async def delete_all_chats_for_user(self, user_id: str) -> int:
        result = await self.chats.delete_many({"user_id": ObjectId(user_id)})
        return result.deleted_count

if __name__ == "__main__":
    async def main():
        
        from dotenv import load_dotenv
        from pathlib import Path
        from os import getenv
        
        env_file = Path(__file__).parent.parent / ".env"
        load_dotenv(env_file)
        DATABASE_USERNAME = getenv("DATABASE_USERNAME")
        DATABASE_PASSWORD = getenv("DATABASE_PASSWORD")
        DATABASE_HOST = getenv("DATABASE_HOST")
        DATABASE_PORT = getenv("DATABASE_PORT")
        
        mongodb = MongoDB(DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)
        await mongodb.create_indexes()

        user_id = await mongodb.create_user("test@example.com", "hashed_password")
        print("Создан пользователь с ID:", user_id)

        chat_id = await mongodb.create_chat(user_id, "Мой первый чат")
        print("Создан чат с ID:", chat_id)

        await mongodb.add_message(chat_id, "user", "text", "Привет!")
        print("Добавлено сообщение в чат.")

        chats = await mongodb.get_chats_for_user(user_id)
        print("Чаты пользователя:", chats)

        messages = await mongodb.get_chat_messages(chat_id)
        print("Сообщения в чате:", messages)

        deleted = await mongodb.delete_chat_for_user(chat_id, user_id)
        print("Чат удалён?", deleted)

        deleted_count = await mongodb.delete_all_chats_for_user(user_id)
        print("Удалено чатов:", deleted_count)

    asyncio.run(main())