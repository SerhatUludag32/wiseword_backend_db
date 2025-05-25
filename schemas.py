from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    email: str
    nickname: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class MessageCreate(BaseModel):
    chat_id: int
    content: str

class ChatResponse(BaseModel):
    chat_id: int
    messages: list