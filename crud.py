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

def get_user_by_google_id(db: Session, google_id: str):
    """Get user by Google ID"""
    return db.query(models.User).filter(models.User.google_id == google_id).first()

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

def create_google_user(db: Session, email: str, nickname: str, google_id: str, profile_picture: str = None):
    """Create a new user from Google OAuth"""
    db_user = models.User(
        email=email,
        nickname=nickname,
        google_id=google_id,
        auth_provider="google",
        is_verified=True,  # Google users are automatically verified
        profile_picture=profile_picture,
        hashed_password=None  # No password for Google users
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

def is_verification_expired(user):
    """Check if user's verification code has expired"""
    if not user or user.is_verified:
        return False
    
    if not user.code_expires_at:
        return True  # No expiration set, consider expired
    
    return datetime.utcnow() > user.code_expires_at

def update_unverified_user(db: Session, existing_user, new_user_data: schemas.UserCreate):
    """Update an existing unverified user with new registration data"""
    # Generate new verification code and expiration
    verification_code = generate_verification_code()
    code_expires_at = datetime.utcnow() + timedelta(minutes=15)
    
    # Update user data
    existing_user.nickname = new_user_data.nickname
    existing_user.hashed_password = pwd_context.hash(new_user_data.password)
    existing_user.verification_code = verification_code
    existing_user.code_expires_at = code_expires_at
    existing_user.is_verified = False
    
    db.commit()
    db.refresh(existing_user)
    return existing_user

def change_password(db: Session, email: str, current_password: str, new_password: str):
    """Change user password after verifying current password"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    # Verify current password
    if not verify_password(current_password, user.hashed_password):
        return False  # Invalid current password
    
    # Hash new password and update
    user.hashed_password = pwd_context.hash(new_password)
    db.commit()
    db.refresh(user)
    return user

def request_password_reset(db: Session, email: str):
    """Generate password reset code and send via email"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    if not user.is_verified:
        return False  # Account not verified
    
    # Generate reset code and set expiration (15 minutes)
    reset_code = generate_verification_code()
    code_expires_at = datetime.utcnow() + timedelta(minutes=15)
    
    # Store reset code in verification_code field (reusing existing field)
    user.verification_code = reset_code
    user.code_expires_at = code_expires_at
    
    db.commit()
    db.refresh(user)
    return user

def reset_password_with_code(db: Session, email: str, reset_code: str, new_password: str):
    """Reset password using email and reset code"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    if not user.is_verified:
        return False  # Account not verified
    
    # Check if reset code matches and hasn't expired
    if (user.verification_code == reset_code and 
        user.code_expires_at and 
        datetime.utcnow() < user.code_expires_at):
        
        # Reset password
        user.hashed_password = pwd_context.hash(new_password)
        user.verification_code = None  # Clear the reset code
        user.code_expires_at = None    # Clear expiration
        
        db.commit()
        db.refresh(user)
        return user
    
    return False  # Invalid or expired code

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

def get_user_chats_with_details(db: Session, user_id: int):
    """Get user chats with message counts and last message info"""
    chats = db.query(models.Chat).filter(models.Chat.user_id == user_id).order_by(models.Chat.created_at.desc()).all()
    
    chat_details = []
    for chat in chats:
        # Get message count and last message
        messages = db.query(models.Message).filter(models.Message.chat_id == chat.id).order_by(models.Message.timestamp.desc()).all()
        
        last_message = None
        last_activity = None
        if messages:
            last_message = messages[0].content[:50] + "..." if len(messages[0].content) > 50 else messages[0].content
            last_activity = messages[0].timestamp
        
        chat_details.append({
            'chat': chat,
            'message_count': len(messages),
            'last_message': last_message,
            'last_activity': last_activity
        })
    
    return chat_details

def get_chat_by_id_and_user(db: Session, chat_id: int, user_id: int):
    """Get chat only if it belongs to the specified user"""
    return db.query(models.Chat).filter(
        models.Chat.id == chat_id,
        models.Chat.user_id == user_id
    ).first()

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