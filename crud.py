from sqlalchemy.orm import Session
import models, schemas
from passlib.context import CryptContext
from datetime import datetime, timedelta
import random
import string
from email_service import email_service

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_verification_code():
    """Generate a 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))

# User operations
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_verification_code(db: Session, code: str):
    return db.query(models.User).filter(models.User.verification_code == code).first()

def create_user(db: Session, user: schemas.UserCreate):
    # Generate verification code and set expiration (15 minutes)
    verification_code = generate_verification_code()
    code_expires_at = datetime.utcnow() + timedelta(minutes=15)
    
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        email=user.email,
        nickname=user.nickname,
        hashed_password=hashed_password,
        is_verified=False,
        verification_code=verification_code,
        code_expires_at=code_expires_at
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_user_email_with_code(db: Session, email: str, verification_code: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    # Check if code matches and hasn't expired
    if (user.verification_code == verification_code and 
        user.code_expires_at and 
        datetime.utcnow() < user.code_expires_at):
        
        user.is_verified = True
        user.verification_code = None  # Clear the code
        user.code_expires_at = None    # Clear expiration
        db.commit()
        db.refresh(user)
        return user
    return None

def resend_verification_code(db: Session, email: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    if user.is_verified:
        return user  # Already verified
    
    # Generate new code and expiration
    user.verification_code = generate_verification_code()
    user.code_expires_at = datetime.utcnow() + timedelta(minutes=15)
    db.commit()
    db.refresh(user)
    return user

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