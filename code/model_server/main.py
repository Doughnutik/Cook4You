from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from logger import logger
from client import client
from schemas.schemas import AuthData, AuthTokenResponse
from pathlib import Path
from dotenv import load_dotenv
from os import getenv
from jwt.jwt import create_access_token, verify_token
from datetime import timedelta

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
    
    
@app.post("/register")
async def register(auth_data: AuthData):
    email = auth_data.email
    password = auth_data.password

    if not email or not password:
        raise HTTPException(status_code=400, detail="неверный формат запроса")

    exists = await client.check_user_existance(email)
    if exists:
        raise HTTPException(status_code=409, detail="email уже существует")
    user_id = await client.new_user(email, password)
    
    token = create_access_token(data={"user_id": user_id})
    return {"user_id": user_id, "token": token}

@app.post("/login")
async def login(auth_data: AuthData):
    email = auth_data.email
    password = auth_data.password

    if not email or not password:
        raise HTTPException(status_code=400, detail="неверный формат запроса")

    user_id = await client.get_user_id(email, password)
    if len(user_id) == 0:
        raise HTTPException(status_code=401, detail="неверный email или пароль")

    token = create_access_token(data={"user_id": user_id})
    return {"user_id": user_id, "token": token}

@app.get("/me")
async def get_me(user_id: str = Depends(verify_token)):
    return {"message": f"Привет, пользователь {user_id}!"}

if __name__ == "__main__":
    logger.info("Сервер запущен на порту: %d", int(MODEL_SERVER_PORT))
    logger.info(f"http://{MODEL_SERVER_HOST}:{MODEL_SERVER_PORT}/docs")
    uvicorn.run(
        app,
        host=MODEL_SERVER_HOST,
        port=int(MODEL_SERVER_PORT),
        log_level="info",
    )
# curl -X GET http://localhost:8080/me \
#   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjgwYmE0N2ZiMzIyODdkOWRlNjgzNGEwIiwiZXhwIjoxNzQ1NjA0MzMxfQ.U5OY8XYihgkRKiq6OZYPCv-2pEWxso5gh9YbGPHBGYk"