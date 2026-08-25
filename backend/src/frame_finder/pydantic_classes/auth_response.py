from pydantic import BaseModel

class AuthResponse(BaseModel):
    email: str
    access_token: str
    refresh_token: str
