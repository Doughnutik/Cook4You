from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
from logger import logger
from client import client
from schemas.schemas import *
from pathlib import Path
from dotenv import load_dotenv
from os import getenv
from jwt_token.jwt_token import create_access_token, verify_token

env_file = Path(__file__).parent.parent / ".env"
load_dotenv(env_file)
MODEL_SERVER_HOST = getenv("MODEL_SERVER_HOST")
MODEL_SERVER_PORT = getenv("MODEL_SERVER_PORT")
SITE_SERVER_HOST = getenv("SITE_SERVER_HOST")
SITE_SERVER_PORT = getenv("SITE_SERVER_PORT")


# Создаем экземпляр приложения FastAPI
app = FastAPI()

# Добавляем CORS для разрешения запросов с твоего фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://{SITE_SERVER_HOST}:{SITE_SERVER_PORT}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register", response_model=AuthTokenResponse)
async def register(auth_data: AuthData):
    email = auth_data.email
    password = auth_data.password

    if not email or not password:
        raise HTTPException(status_code=400, detail="неверный формат запроса")

    exists = await client.check_user_existance(email)
    if exists:
        raise HTTPException(status_code=409, detail="email уже существует")
    user_id = await client.new_user(email, password)
    if len(user_id) == 0:
        raise HTTPException(status_code=500, detail="ошибка создания пользователя")
    
    token = create_access_token(data={"user_id": user_id})
    return AuthTokenResponse(token=token)

@app.post("/login", response_model=AuthTokenResponse)
async def login(auth_data: AuthData):
    email = auth_data.email
    password = auth_data.password

    if not email or not password:
        raise HTTPException(status_code=400, detail="неверный формат запроса")

    user_id = await client.get_user_id(email, password)
    if len(user_id) == 0:
        raise HTTPException(status_code=401, detail="неверные email или пароль")

    token = create_access_token(data={"user_id": user_id})
    return AuthTokenResponse(token=token)

@app.get("/chats", response_model=list[ChatData])
async def get_all_chats(user_id: str = Depends(verify_token)):
    chats = await client.get_user_chats(user_id)
    result = []
    for chat in chats:
        result.append(ChatData(chat_id=str(chat['_id']),
                               title=chat['title'],
                               created_at=chat['created_at'],
                               updated_at=chat['updated_at'],
                               messages=chat['messages']))
    return result

@app.delete("/chats")
async def delete_all_chats(user_id: str = Depends(verify_token)):
    result = await client.delete_all_user_chats(user_id)
    if not result:
        raise HTTPException(status_code=500, detail="ошибка удаления чатов")
    
@app.post("/chat", response_model=ChatData)
async def create_chat(data: CreateUpdateChat, user_id: str = Depends(verify_token)):
    chat_id = await client.new_chat(user_id, data.title)
    if len(chat_id) == 0:
        raise HTTPException(status_code=500, detail="ошибка создания чата")
    chat = await client.get_chat(chat_id)
    if len(chat) == 0:
        raise HTTPException(status_code=500, detail="ошибка получения чата")
    return ChatData(chat_id=chat_id,
                    title=chat['title'],
                    created_at=chat['created_at'],
                    updated_at=chat['updated_at'],
                    messages=chat['messages'])

@app.get("/chat/{chat_id}", response_model=ChatData)
async def get_chat(chat_id: str, user_id: str = Depends(verify_token)):
    auth_correct = await client.chat_exists_for_user(chat_id, user_id)
    if not auth_correct:
        raise HTTPException(status_code=404, detail="чат для данного пользователя не найден")
    chat = await client.get_chat(chat_id)
    if len(chat) == 0:
        raise HTTPException(status_code=500, detail="ошибка получения чата")
    return ChatData(chat_id=chat_id,
                    title=chat['title'],
                    created_at=chat['created_at'],
                    updated_at=chat['updated_at'],
                    messages=chat['messages'])

@app.delete("/chat/{chat_id}")
async def delete_chat(chat_id: str, user_id: str = Depends(verify_token)):
    auth_correct = await client.chat_exists_for_user(chat_id, user_id)
    if not auth_correct:
        raise HTTPException(status_code=404, detail="чат для данного пользователя не найден")
    result = await client.delete_chat(chat_id, user_id)
    if not result:
        raise HTTPException(status_code=500, detail="ошибка удаления чата")

@app.post("/chat/{chat_id}/add-message", response_model=ChatData)
async def add_message_to_chat(chat_id: str, message: MessageData, user_id: str = Depends(verify_token)):
    auth_correct = await client.chat_exists_for_user(chat_id, user_id)
    if not auth_correct:
        raise HTTPException(status_code=404, detail="чат для данного пользователя не найден")
    result = await client.add_message(chat_id, message.role, message.type, message.content)
    if not result:
        raise HTTPException(status_code=500, detail="ошибка добавления сообщения в чат")
    chat = await client.get_chat(chat_id)
    if len(chat) == 0:
        raise HTTPException(status_code=500, detail="ошибка получения чата")
    return ChatData(chat_id=chat_id,
                    title=chat['title'],
                    created_at=chat['created_at'],
                    updated_at=chat['updated_at'],
                    messages=chat['messages'])
    
@app.get("/chat/{chat_id}/model-answer-text", response_model=MessageData)
async def get_chat(chat_id: str, user_id: str = Depends(verify_token)):
    auth_correct = await client.chat_exists_for_user(chat_id, user_id)
    if not auth_correct:
        raise HTTPException(status_code=404, detail="чат для данного пользователя не найден")
    response = await client.ask_question(user_id, chat_id, 'text')
    if len(response) == 0:
        raise HTTPException(status_code=500, detail="ошибка получения ответа модели")
    return MessageData(role=RoleEnum.assistant, type=TypeEnum.text, content=response)

@app.get("/chat/{chat_id}/model-answer-image", response_model=MessageData)
async def get_chat(chat_id: str, user_id: str = Depends(verify_token)):
    auth_correct = await client.chat_exists_for_user(chat_id, user_id)
    if not auth_correct:
        raise HTTPException(status_code=404, detail="чат для данного пользователя не найден")
    response = await client.ask_question(user_id, chat_id, 'image')
    if len(response) == 0:
        raise HTTPException(status_code=500, detail="ошибка получения ссылки на изображение")
    return MessageData(role=RoleEnum.assistant, type=TypeEnum.image, content=response)
    
async def main():
    logger.info("Сервер запущен")
    id = "-"
    while id == "-":
        email = input("Введите email: ")
        password = input("Введите пароль: ")
        id = await client.get_user_id(email, password)
        if len(id) == 0:
            id = await client.new_user(email, password)
        elif id == "-":
            print("Неверный пароль, попробуйте снова")
    
    chats = await client.get_user_chats(id)
    print()
    print(chats)
    print()
    
    chat_id = input("Введите chat_id: ")
    if chat_id == "-":
        title = input("Введите название нового чата: ")
        chat_id = await client.new_chat(id, title)
    while True:
        user_input = input("Ваш вопрос: ")
        if user_input == "exit":
            break
        elif user_input == "image":
            url = await client.ask_question(id, chat_id, '', "image")
            print(f"Ссылка на картинку: {url}")
        else:
            response = await client.ask_question(id, chat_id, user_input, "text")
            print(f"Ответ модели: {response}")

if __name__ == "__main__":
    logger.info("Сервер запущен на порту: %d", int(MODEL_SERVER_PORT))
    logger.info(f"http://{MODEL_SERVER_HOST}:{MODEL_SERVER_PORT}/docs")
    uvicorn.run(
        app,
        host=MODEL_SERVER_HOST,
        port=int(MODEL_SERVER_PORT),
        log_level="info",
    )
    # asyncio.run(main())

# curl -X 'GET' \
#   'http://localhost:8080/chat/68236f61f797d375cab54c7d/model-answer-image' \
#   -H 'accept: application/json' \
#   -H 'Content-Type: application/json' \
#   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjgxZDZkODI0OTg1YTM0YWRkOTc0YTZjIiwiZXhwIjoxNzQ3MTUzMjQ0fQ.U6pVsc0YtKdmEpVCfpfkLKkRXKRJoekWGGlBhYx8GlA" \
#   -d '{
#   "role": "user",
#   "type": "text",
#   "content": "Хочу приготовить салат цезарь",
#   "created_at": "2025-05-13T19:10:22.849456"
# }'


#TODO 1) Добавить кнопку "выйти", чтобы поменять учётную запись
#TODO 2) Разобраться, как поднять всё это на удалённом серваке (оба сервака + бд)
#TODO 3) Почистить код от мусора, почистить бд, если нужно, почистить логи. Загрузить на сервак чистое приложение.
#TODO 4) Догрузить все необходимые библиотеки в requirements.txt, загрузить финальный коммит в репозиторий, оформить Readme с полноценной инструкцией по локальному запуску

#Тесты на 10 пользователях
#1:40 - текст
#2:40 - изображение