import motor.motor_asyncio
from bson import ObjectId
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from os import getenv

env_file = Path(__file__).parent.parent / ".env"
load_dotenv(env_file)
DATABASE_HOST = getenv("DATABASE_HOST")
DATABASE_PORT = getenv("DATABASE_PORT")

# Инициализация клиента
client = motor.motor_asyncio.AsyncIOMotorClient(f"mongodb://{DATABASE_HOST}:{DATABASE_PORT}")
db = client["Cook4You"]
users = db["users"]
chats = db["chats"]

# Нужен индекс для поиска чатов пользователя
async def create_indexes():
    await chats.create_index("user_id")

# Создание нового пользователя
async def create_user(email: str, password_hash: str) -> str:
    user = {
        "email": email,
        "password_hash": password_hash,
        "created_at": datetime.now()
    }
    result = await users.insert_one(user)
    return str(result.inserted_id)

# Создание нового чата
async def create_chat(user_id: str, title: str) -> str:
    chat = {
        "user_id": ObjectId(user_id),
        "title": title,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "messages": []
    }
    result = await chats.insert_one(chat)
    return str(result.inserted_id)

# Добавление сообщения в чат
async def add_message(chat_id: str, sender: str, type: str, content: str) -> bool:
    message = {
        "sender": sender,
        "type": type,  # "text" или "image"
        "content": content, # "text" или "url"
        "created_at": datetime.now()
    }
    result = await chats.update_one(
        {"_id": ObjectId(chat_id)},
        {
            "$push": {"messages": message},
            "$set": {"updated_at": datetime.now()}
        }
    )
    return result.modified_count > 0

# Получение всех чатов пользователя
async def get_chats_for_user(user_id: str):
    cursor = chats.find({"user_id": ObjectId(user_id)}, {"messages": 0})  # Без сообщений
    return [chat async for chat in cursor]

# Получение сообщений конкретного чата
async def get_chat_messages(chat_id: str):
    chat = await chats.find_one({"_id": ObjectId(chat_id)}, {"messages": 1})
    return chat["messages"] if chat else []

# Удаление чата пользователя
async def delete_chat_for_user(chat_id: str, user_id: str) -> bool:
    result = await chats.delete_one({
        "_id": ObjectId(chat_id),
        "user_id": ObjectId(user_id)
    })
    return result.deleted_count == 1

# Удаление всех чатов пользователя
async def delete_all_chats_for_user(user_id: str) -> int:
    result = await chats.delete_many({"user_id": ObjectId(user_id)})
    return result.deleted_count