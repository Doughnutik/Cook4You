from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Optional


class AuthData(BaseModel):
    email: str
    password: str
    
class AuthTokenResponse(BaseModel):
    token: str
    
class RoleEnum(str, Enum):
    user = "user"
    assistant = "assistant"
    
class TypeEnum(str, Enum):
    text = "text"
    image = "image"
    
class MessageData(BaseModel):
    role: Optional[RoleEnum] = RoleEnum.user
    type: Optional[TypeEnum] = TypeEnum.text
    content: str
    created_at: Optional[datetime] = datetime.now()
    
class ChatData(BaseModel):
    chat_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageData]
    
class CreateUpdateChat(BaseModel):
    title: str