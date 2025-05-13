from typing import Literal
from model.model import Model
from storage.mongo_async import MongoDB
import bcrypt
from pathlib import Path
from dotenv import load_dotenv
from os import getenv

env_file = Path(__file__).parent.parent / ".env"
load_dotenv(env_file)
INITIAL_PROMPT = getenv("INITIAL_PROMPT")

class Client:
    def __init__(self, model: Model, storage: MongoDB, logger):
        self.model = model
        self.storage = storage
        self.logger = logger
        self.logger.info("Создан клиент для обработки запросов")

    async def ask_question(self, user_id: str, chat_id: str, type: Literal["text", "image"]) -> str:
        """
        Обрабатывает запрос пользователя
        """
        if not await self.storage.user_id_exists(user_id):
            return ""
        if not await self.storage.chat_exists_for_user(chat_id, user_id):
            return ""
        
        match type:
            case "text":
                return await self.generate_response(chat_id)
            case "image":
                return await self.generate_image(chat_id)
            case _:
                logger.warning("ask_question: пришёл неизвестный тип вопроса")
                return ""

    async def generate_response(self, chat_id: str) -> str:
        """
        Генерирует ответ на вопрос пользователя.
        """
        history = await self.storage.get_chat_messages(chat_id)
        if len(history) == 0:
            return ""
        
        result = await self.model.response(history)
        if len(result) == 0:
            return ""
        
        success = await self.storage.add_message(chat_id, "assistant", "text", result)
        if not success:
            self.logger.error(f"generate_response: ошибка добавления ответа модели:\n{result}")
            return ""
        
        return result
    
    async def generate_image(self, chat_id: str) -> str:
        """
        Создаёт изображение на основе истории сообщений.
        """
        history = await self.storage.get_chat_messages(chat_id)
        if len(history) == 0:
            return ""
        
        result = await self.model.image(history)
        if len(result) == 0:
            return ""
        
        success = await self.storage.add_message(chat_id, "assistant", "image", result)
        if not success:
            self.logger.error(f"generate_image: ошибка добавления ответа модели:\n{result}")
            return ""
        
        return result
    
    async def new_user(self, email: str, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return await self.storage.create_user(email, hashed.decode())
    
    async def get_user_id(self, email: str, password: str) -> str:
        return await self.storage.get_user_id(email, password)
    
    async def check_user_existance(self, email: str) -> bool:
        return await self.storage.user_exists(email)

    async def new_chat(self, user_id: str, title: str) -> str:
        chat_id = await self.storage.create_chat(user_id=user_id, title=title)
        success = await self.storage.add_message(chat_id, "user", "text", INITIAL_PROMPT)
        if not success:
            self.logger.error(f"new_chat: не получилось добавить initial prompt.\n"
                              "chat_id = {chat_id}, user_id = {user_id}, title = {title}")
            return ""
        return chat_id

    async def get_user_chats(self, user_id: str):
        return await self.storage.get_chats_for_user(user_id)

    async def get_chat_history(self, chat_id: str):
        return await self.storage.get_chat_messages(chat_id)
    
    async def get_chat(self, chat_id: str):
        return await self.storage.get_chat(chat_id)

    async def delete_chat(self, chat_id: str, user_id: str) -> bool:
        return await self.storage.delete_chat_for_user(chat_id, user_id)

    async def delete_all_user_chats(self, user_id: str) -> bool:
        return await self.storage.delete_all_chats_for_user(user_id)
    
    async def user_id_exists(self, user_id: str) -> bool:
        return await self.storage.user_id_exists(user_id)
    
    async def chat_exists_for_user(self, chat_id: str, user_id: str) -> bool:
        return await self.storage.chat_exists_for_user(chat_id, user_id)
    
    async def rename_chat(self, chat_id: str, title: str) -> bool:
        return await self.storage.rename_chat(chat_id, title)
    
    async def add_message(self, chat_id: str, role: str, type: str, content: str) -> bool:
        return await self.storage.add_message(chat_id, role, type, content)