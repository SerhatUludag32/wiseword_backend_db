from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import SessionLocal
import crud, schemas
import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY")  # 🔒 Now reads from .env file for security
ALGORITHM = "HS256"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post(
    "/register", 
    response_model=schemas.RegisterResponse,
    summary="📝 Register New User",
    description="Create a new user account and send verification code via email",
    responses={
        200: {"description": "User registered successfully", "model": schemas.RegisterResponse},
        400: {"description": "Email already registered", "model": schemas.ErrorResponse},
        422: {"description": "Validation error", "model": schemas.ValidationErrorResponse}
    }
)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400, 
            detail="Email already registered. Try logging in or use a different email."
        )
    
    # Create new user (unverified)
    new_user = crud.create_user(db=db, user=user)
    
    # Send verification email with code
    from email_service import email_service
    email_sent = email_service.send_verification_email(
        to_email=new_user.email,
        verification_code=new_user.verification_code
    )
    
    user_response = schemas.UserResponse(
        id=new_user.id,
        email=new_user.email,
        nickname=new_user.nickname,
        is_verified=new_user.is_verified
    )
    
    if not email_sent:
        return schemas.RegisterResponse(
            message="User registered successfully, but verification email failed to send. Please contact support.",
            email_sent=False,
            user=user_response
        )
    
    return schemas.RegisterResponse(
        message="User registered successfully! Please check your email for verification code.",
        email_sent=True,
        user=user_response
    )

@router.post(
    "/login",
    response_model=schemas.LoginResponse,
    summary="🔐 User Login", 
    description="Authenticate user and receive JWT access token",
    responses={
        200: {"description": "Login successful", "model": schemas.LoginResponse},
        400: {"description": "Invalid credentials or email not verified", "model": schemas.ErrorResponse},
        422: {"description": "Validation error", "model": schemas.ValidationErrorResponse}
    }
)
def login(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    # Get user from database
    db_user = crud.get_user_by_email(db, email=user_login.email)
    if not db_user:
        raise HTTPException(
            status_code=400, 
            detail="Invalid email or password. Please check your credentials."
        )
    
    # Verify password
    if not crud.verify_password(user_login.password, db_user.hashed_password):
        raise HTTPException(
            status_code=400, 
            detail="Invalid email or password. Please check your credentials."
        )
    
    # Check if email is verified
    if not db_user.is_verified:
        raise HTTPException(
            status_code=400, 
            detail="Email not verified. Please check your email and enter the verification code."
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": db_user.email, "user_id": db_user.id})
    
    user_response = schemas.UserResponse(
        id=db_user.id,
        email=db_user.email,
        nickname=db_user.nickname,
        is_verified=db_user.is_verified
    )
    
    return schemas.LoginResponse(
        message="Login successful",
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

@router.post(
    "/verify-code",
    response_model=schemas.VerificationResponse,
    summary="✅ Verify Email Code",
    description="Verify email address using 6-digit code sent via email",
    responses={
        200: {"description": "Email verified successfully", "model": schemas.VerificationResponse},
        400: {"description": "Invalid or expired code", "model": schemas.ErrorResponse},
        422: {"description": "Validation error", "model": schemas.ValidationErrorResponse}
    }
)
def verify_code(verification: schemas.CodeVerification, db: Session = Depends(get_db)):
    # Verify the email with the code
    user = crud.verify_user_email_with_code(db, verification.email, verification.code)
    if not user:
        raise HTTPException(
            status_code=400, 
            detail="Invalid verification code or code has expired. Please request a new one."
        )
    
    # Send welcome email
    from email_service import email_service
    email_service.send_welcome_email(user.email, user.nickname)
    
    user_response = schemas.UserResponse(
        id=user.id,
        email=user.email,
        nickname=user.nickname,
        is_verified=user.is_verified
    )
    
    return schemas.VerificationResponse(
        message="Email verified successfully! Welcome to Wise Words!",
        user=user_response
    )

@router.post(
    "/resend-verification",
    summary="📧 Resend Verification Code",
    description="Request a new verification code if the previous one expired",
    responses={
        200: {"description": "New verification code sent"},
        400: {"description": "Email already verified"},
        404: {"description": "User not found", "model": schemas.ErrorResponse},
        500: {"description": "Failed to send email", "model": schemas.ErrorResponse}
    }
)
def resend_verification(request: schemas.ResendVerification, db: Session = Depends(get_db)):
    # Get user and generate new code
    user = crud.resend_verification_code(db, request.email)
    if not user:
        raise HTTPException(
            status_code=404, 
            detail="User not found. Please register first."
        )
    
    if user.is_verified:
        return {"message": "Email is already verified. You can login directly."}
    
    # Send verification email with new code
    from email_service import email_service
    email_sent = email_service.send_verification_email(
        to_email=user.email,
        verification_code=user.verification_code
    )
    
    if email_sent:
        return {"message": "New verification code sent successfully. Check your email."}
    else:
        raise HTTPException(
            status_code=500, 
            detail="Failed to send verification email. Please try again later."
        )