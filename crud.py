from sqlalchemy.orm import Session
import models, schemas
from passlib.context import CryptContext
from datetime import datetime
from email_service import email_service

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User operations
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_verification_token(db: Session, token: str):
    return db.query(models.User).filter(models.User.verification_token == token).first()

def create_user(db: Session, user: schemas.UserCreate):
    # Generate verification token
    verification_token = email_service.generate_verification_token()
    
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        email=user.email,
        nickname=user.nickname,
        hashed_password=hashed_password,
        is_verified=False,
        verification_token=verification_token
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_user_email(db: Session, verification_token: str):
    user = get_user_by_verification_token(db, verification_token)
    if user:
        user.is_verified = True
        user.verification_token = None  # Clear the token
        db.commit()
        db.refresh(user)
        return user
    return None

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Persona operations
def get_personas(db: Session):
    return db.query(models.Persona).all()

def get_persona_by_id(db: Session, persona_id: int):
    return db.query(models.Persona).filter(models.Persona.id == persona_id).first()

# Chat operations
def create_chat(db: Session, user_id: int, persona_id: int):
    db_chat = models.Chat(user_id=user_id, persona_id=persona_id)
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

def get_user_chats(db: Session, user_id: int):
    return db.query(models.Chat).filter(models.Chat.user_id == user_id).all()

# Message operations
def create_message(db: Session, chat_id: int, sender: str, content: str):
    db_message = models.Message(
        chat_id=chat_id,
        sender=sender,
        content=content
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_chat_messages(db: Session, chat_id: int):
    return db.query(models.Message).filter(models.Message.chat_id == chat_id).order_by(models.Message.timestamp).all()