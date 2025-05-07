from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime
import asyncio
import bcrypt

class MongoDB:
    def __init__(self, username: str, password: str, host: str, port: str, logger):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.logger = logger
        
        self.client = AsyncIOMotorClient(
            f"mongodb://{username}:{password}@{host}:{port}")
        
        self.db = self.client["Cook4You"]
        self.users = self.db["users"]
        self.chats = self.db["chats"]
        
        self.logger.info("Создан Async клиент MongoDB")
        
    # Нужен индекс для поиска чатов пользователя
    async def create_indexes(self):
        try:
            await self.chats.create_index("user_id")
        except Exception as e:
            self.logger.error(f"create_indexes: {e}")
       
    # Проверка наличия пользователя user_id в бд     
    async def user_id_exists(self, user_id: str) -> bool:
        try:
            user = await self.users.find_one({"_id": ObjectId(user_id)})
            return user is not None
        except Exception as e:
            self.logger.error(f"user_id_exists: {e}")
            return False
    
    # Проверка наличия чата у пользователя в бд
    async def chat_exists_for_user(self, chat_id: str, user_id: str) -> bool:
        try:
            chat = await self.chats.find_one({
                "_id": ObjectId(chat_id),
                "user_id": ObjectId(user_id)
            })
            return chat is not None
        except Exception as e:
            self.logger.error(f"chat_exists_for_user: {e}")
            return False

    # Создание нового пользователя
    async def create_user(self, email: str, password_hash: str) -> str:
        try:
            user = {
                "email": email,
                "password_hash": password_hash,
                "created_at": datetime.now().isoformat()
            }
            result = await self.users.insert_one(user)
            return str(result.inserted_id)
        except Exception as e:
            self.logger.error(f"create_user: {e}")
            return ""

    # Создание нового чата
    async def create_chat(self, user_id: str, title: str) -> str:
        try:
            chat = {
                "user_id": ObjectId(user_id),
                "title": title,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "messages": []
            }
            result = await self.chats.insert_one(chat)
            return str(result.inserted_id)
        except Exception as e:
            self.logger.error(f"create_chat: {e}")
            return ""

    # Добавление сообщения в чат
    async def add_message(self, chat_id: str, role: str, type: str, content: str) -> bool:
        try:
            message = {
                "role": role,
                "type": type,  # "text" или "image"
                "content": content, # "text" или "url"
                "created_at": datetime.now().isoformat()
            }
            result = await self.chats.update_one(
                {"_id": ObjectId(chat_id)},
                {
                    "$push": {"messages": message},
                    "$set": {"updated_at": datetime.now().isoformat()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            self.logger.error(f"add_message: {e}")
            return False

    # Получение всех чатов пользователя
    async def get_chats_for_user(self, user_id: str):
        try:
            cursor = self.chats.find({"user_id": ObjectId(user_id)}, {"user_id": 0}) # Без user_id
            return [chat async for chat in cursor]
        except Exception as e:
            self.logger.error(f"get_chats_for_user: {e}")
            return []

    # Получение сообщений конкретного чата
    async def get_chat_messages(self, chat_id: str):
        try:
            chat = await self.chats.find_one({"_id": ObjectId(chat_id)}, {"messages": 1})
            return chat["messages"] if chat else []
        except Exception as e:
            self.logger.error(f"get_chat_messages: {e}")
            return []
        
    # Получение конкретного чата
    async def get_chat(self, chat_id: str):
        try:
            chat = await self.chats.find_one({"_id": ObjectId(chat_id)})
            return chat if chat else {}
        except Exception as e:
            self.logger.error(f"get_chat: {e}")
            return {}

    # Удаление чата пользователя
    async def delete_chat_for_user(self, chat_id: str, user_id: str) -> bool:
        try:
            result = await self.chats.delete_one({
                "_id": ObjectId(chat_id),
                "user_id": ObjectId(user_id)
            })
            return result.deleted_count == 1
        except Exception as e:
            self.logger.error(f"delete_chat_for_user: {e}")
            return False

    # Удаление всех чатов пользователя
    async def delete_all_chats_for_user(self, user_id: str) -> bool:
        try:
            cnt = await self.chats.count_documents({"user_id": ObjectId(user_id)})
            result = await self.chats.delete_many({"user_id": ObjectId(user_id)})
            return result.deleted_count == cnt
        except Exception as e:
            self.logger.error(f"delete_all_chats_for_user: {e}")
            return False
        
    # Получение user_id по email и password
    async def get_user_id(self, email: str, password: str) -> str:
        try:
            user = await self.users.find_one({"email": email})
            if not user:
                return ""
            
            password_hash = user.get("password_hash", "").encode()
            if bcrypt.checkpw(password.encode(), password_hash):
                return str(user["_id"])
            else:
                return ""
        except Exception as e:
            self.logger.error(f"get_user_id: {e}")
            return ""
    
    # Проверка существования email в бд
    async def user_exists(self, email: str) -> bool:
        try:
            user = await self.users.find_one({"email": email})
            return user is not None
        except Exception as e:
            self.logger.error(f"user_exists: {e}")
            return False
        
    async def rename_chat(self, chat_id: str, new_title: str) -> bool:
        try:
            result = await self.chats.update_one(
                {"_id": ObjectId(chat_id)},
                {"$set": {"title": new_title}}
            )
            return result.modified_count == 1
        except Exception as e:
            self.logger.error(f"rename_chat: {e}")
            return False
            

if __name__ == "__main__":
    async def main():
        
        from dotenv import load_dotenv
        from pathlib import Path
        from os import getenv
        from logger import logger
        
        env_file = Path(__file__).parent.parent / ".env"
        load_dotenv(env_file)
        DATABASE_USERNAME = getenv("DATABASE_USERNAME")
        DATABASE_PASSWORD = getenv("DATABASE_PASSWORD")
        DATABASE_HOST = getenv("DATABASE_HOST")
        DATABASE_PORT = getenv("DATABASE_PORT")
        
        mongodb = MongoDB(DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT, logger)
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