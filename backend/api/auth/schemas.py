from pydantic import BaseModel

class LoginScheme(BaseModel):
    username: str
    password: str

class TokenResponseScheme(BaseModel):
    access_token: str
    token_type: str = "bearer"