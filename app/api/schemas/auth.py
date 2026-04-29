from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    senha: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    nome: str
    role: str
