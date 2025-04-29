from pydantic import BaseModel

class AuthData(BaseModel):
    email: str
    password: str
    
class AuthTokenResponse(BaseModel):
    token: str
    user_id: str