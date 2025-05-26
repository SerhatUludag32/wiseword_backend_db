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
    description="Create a new user account and send verification code via email. If email exists but verification expired, updates the account with new data.",
    responses={
        200: {"description": "User registered successfully or existing unverified account updated", "model": schemas.RegisterResponse},
        400: {"description": "Email already verified or registration blocked", "model": schemas.ErrorResponse},
        422: {"description": "Validation error", "model": schemas.ValidationErrorResponse}
    }
)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    
    if db_user:
        # If user is verified, block registration
        if db_user.is_verified:
            raise HTTPException(
                status_code=400, 
                detail="Email already registered and verified. Please login instead."
            )
        
        # If user is unverified but verification hasn't expired, suggest resend
        if not crud.is_verification_expired(db_user):
            raise HTTPException(
                status_code=400, 
                detail="Email already registered but not verified. Please check your email for verification code or use /auth/resend-verification."
            )
        
        # If user is unverified and verification expired, update existing account
        new_user = crud.update_unverified_user(db, db_user, user)
    else:
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
    
    # Determine appropriate message
    if db_user and not db_user.is_verified:
        success_message = "Registration updated! Previous verification expired. Please check your email for new verification code."
    else:
        success_message = "User registered successfully! Please check your email for verification code."
    
    if not email_sent:
        return schemas.RegisterResponse(
            message="Registration completed, but verification email failed to send. Please contact support.",
            email_sent=False,
            user=user_response
        )
    
    return schemas.RegisterResponse(
        message=success_message,
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

@router.post(
    "/change-password",
    response_model=schemas.PasswordChangeResponse,
    summary="🔑 Change Password",
    description="Change user password by providing current password and new password",
    responses={
        200: {"description": "Password changed successfully", "model": schemas.PasswordChangeResponse},
        400: {"description": "Invalid current password or user not found", "model": schemas.ErrorResponse},
        422: {"description": "Validation error", "model": schemas.ValidationErrorResponse}
    }
)
def change_password(password_change: schemas.PasswordChange, db: Session = Depends(get_db)):
    # Attempt to change password
    result = crud.change_password(
        db=db, 
        email=password_change.email,
        current_password=password_change.current_password,
        new_password=password_change.new_password
    )
    
    if result is None:
        raise HTTPException(
            status_code=400, 
            detail="User not found. Please check your email address."
        )
    
    if result is False:
        raise HTTPException(
            status_code=400, 
            detail="Current password is incorrect. Please try again."
        )
    
    # Password changed successfully
    user_response = schemas.UserResponse(
        id=result.id,
        email=result.email,
        nickname=result.nickname,
        is_verified=result.is_verified
    )
    
    return schemas.PasswordChangeResponse(
        message="Password changed successfully!",
        user=user_response
    )

@router.post(
    "/forgot-password",
    response_model=schemas.ForgotPasswordResponse,
    summary="🔐 Forgot Password",
    description="Request password reset code via email for users who forgot their password",
    responses={
        200: {"description": "Reset code sent successfully", "model": schemas.ForgotPasswordResponse},
        400: {"description": "User not found or account not verified", "model": schemas.ErrorResponse},
        422: {"description": "Validation error", "model": schemas.ValidationErrorResponse}
    }
)
def forgot_password(request: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    # Request password reset
    result = crud.request_password_reset(db, request.email)
    
    if result is None:
        raise HTTPException(
            status_code=400, 
            detail="No account found with this email address."
        )
    
    if result is False:
        raise HTTPException(
            status_code=400, 
            detail="Account not verified. Please verify your email first before resetting password."
        )
    
    # Send password reset email
    from email_service import email_service
    email_sent = email_service.send_password_reset_email(
        to_email=result.email,
        reset_code=result.verification_code
    )
    
    if email_sent:
        return schemas.ForgotPasswordResponse(
            message="Password reset code sent to your email! Check your inbox.",
            email_sent=True
        )
    else:
        raise HTTPException(
            status_code=500, 
            detail="Failed to send reset email. Please try again later."
        )

@router.post(
    "/reset-password",
    response_model=schemas.ResetPasswordResponse,
    summary="🔓 Reset Password",
    description="Reset password using email, reset code, and new password",
    responses={
        200: {"description": "Password reset successfully", "model": schemas.ResetPasswordResponse},
        400: {"description": "Invalid reset code or user not found", "model": schemas.ErrorResponse},
        422: {"description": "Validation error", "model": schemas.ValidationErrorResponse}
    }
)
def reset_password(reset_data: schemas.ResetPasswordConfirm, db: Session = Depends(get_db)):
    # Reset password with code
    result = crud.reset_password_with_code(
        db=db,
        email=reset_data.email,
        reset_code=reset_data.reset_code,
        new_password=reset_data.new_password
    )
    
    if result is None:
        raise HTTPException(
            status_code=400, 
            detail="No account found with this email address."
        )
    
    if result is False:
        raise HTTPException(
            status_code=400, 
            detail="Invalid or expired reset code. Please request a new password reset."
        )
    
    # Password reset successfully
    user_response = schemas.UserResponse(
        id=result.id,
        email=result.email,
        nickname=result.nickname,
        is_verified=result.is_verified
    )
    
    return schemas.ResetPasswordResponse(
        message="Password reset successfully! You can now login with your new password.",
        user=user_response
    )