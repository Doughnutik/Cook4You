from datetime import datetime, timedelta
from jose import JWTError, jwt, ExpiredSignatureError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pathlib import Path
from dotenv import load_dotenv
from os import getenv

env_file = Path(__file__).parent.parent / ".env"
load_dotenv(env_file)
JWT_SECRET = getenv("JWT_SECRET")
JWT_ALGO = getenv("JWT_ALGO")
JWT_TIME = int(getenv("JWT_TIME", 10))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=JWT_TIME)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, key=JWT_SECRET, algorithm=JWT_ALGO)
    return encoded_jwt

def verify_token(token: str = Depends(oauth2_scheme)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="неверный или отсутствующий токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        return user_id
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="токен истёк")
    except JWTError:
        raise credentials_exception