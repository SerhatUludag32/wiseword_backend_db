from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    nickname = Column(String)
    hashed_password = Column(String, nullable=True)  # Nullable for Google OAuth users
    is_verified = Column(Boolean, default=False)
    verification_code = Column(String(6), nullable=True)  # 6-digit verification code
    code_expires_at = Column(DateTime, nullable=True)     # Code expiration time
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Google OAuth fields
    google_id = Column(String, nullable=True, unique=True)  # Google user ID
    auth_provider = Column(String, default="email")  # "email" or "google"
    profile_picture = Column(String, nullable=True)  # Google profile picture URL

class Persona(Base):
    __tablename__ = "personas"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text)
    prompt = Column(Text)

class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    persona_id = Column(Integer, ForeignKey("personas.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    sender = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)