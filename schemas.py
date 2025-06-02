from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# Request Models
class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="Valid email address", example="user@example.com")
    nickname: str = Field(..., min_length=2, max_length=50, description="Display name", example="John Doe")
    password: str = Field(..., min_length=6, description="Password (minimum 6 characters)", example="secure123")

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Registered email address", example="user@example.com") 
    password: str = Field(..., description="User password", example="secure123")

class CodeVerification(BaseModel):
    email: EmailStr = Field(..., description="Email address to verify", example="user@example.com")
    code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code", example="123456")

class ResendVerification(BaseModel):
    email: EmailStr = Field(..., description="Email to resend verification code", example="user@example.com")

class PasswordChange(BaseModel):
    email: EmailStr = Field(..., description="User email address", example="user@example.com")
    current_password: str = Field(..., min_length=6, description="Current password", example="oldpassword123")
    new_password: str = Field(..., min_length=6, description="New password (minimum 6 characters)", example="newpassword123")

class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Email address to send reset code", example="user@example.com")

class ResetPasswordConfirm(BaseModel):
    email: EmailStr = Field(..., description="Email address", example="user@example.com")
    reset_code: str = Field(..., min_length=6, max_length=6, description="6-digit reset code from email", example="123456")
    new_password: str = Field(..., min_length=6, description="New password (minimum 6 characters)", example="newpassword123")

class MessageCreate(BaseModel):
    chat_id: int = Field(..., gt=0, description="ID of the chat session", example=1)
    content: str = Field(..., min_length=1, max_length=2000, description="Message content", example="Hello Einstein!")

# Response Models
class UserResponse(BaseModel):
    id: int = Field(..., description="User ID", example=1)
    email: str = Field(..., description="User email", example="user@example.com")
    nickname: str = Field(..., description="User display name", example="John Doe")
    is_verified: bool = Field(..., description="Email verification status", example=True)
    auth_provider: str = Field(..., description="Authentication provider", example="email")
    profile_picture: Optional[str] = Field(None, description="Profile picture URL", example="https://lh3.googleusercontent.com/...")

class LoginResponse(BaseModel):
    message: str = Field(..., description="Success message", example="Login successful")
    access_token: str = Field(..., description="JWT access token", example="eyJhbGciOiJIUzI1NiIs...")
    token_type: str = Field(..., description="Token type", example="bearer")
    user: UserResponse

class RegisterResponse(BaseModel):
    message: str = Field(..., description="Registration result", example="User registered successfully!")
    email_sent: bool = Field(..., description="Whether verification email was sent", example=True)
    user: UserResponse

class VerificationResponse(BaseModel):
    message: str = Field(..., description="Verification result", example="Email verified successfully!")
    user: UserResponse

class PasswordChangeResponse(BaseModel):
    message: str = Field(..., description="Password change result", example="Password changed successfully!")
    user: UserResponse

class ForgotPasswordResponse(BaseModel):
    message: str = Field(..., description="Forgot password result", example="Reset code sent to your email!")
    email_sent: bool = Field(..., description="Whether reset email was sent", example=True)

class ResetPasswordResponse(BaseModel):
    message: str = Field(..., description="Password reset result", example="Password reset successfully!")
    user: UserResponse

class PersonaResponse(BaseModel):
    id: int = Field(..., description="Persona ID", example=1)
    name: str = Field(..., description="Historical figure name", example="Albert Einstein")
    description: str = Field(..., description="Brief description", example="Theoretical physicist")

class PersonasListResponse(BaseModel):
    personas: List[PersonaResponse] = Field(..., description="Available historical figures")

class ChatStartResponse(BaseModel):
    message: str = Field(..., description="Chat start confirmation", example="Chat started")
    chat_id: int = Field(..., description="Chat session ID", example=1)
    persona: PersonaResponse

class MessageResponse(BaseModel):
    id: int = Field(..., description="Message ID", example=1)
    sender: str = Field(..., description="Message sender", example="user")
    content: str = Field(..., description="Message content", example="Hello!")
    timestamp: datetime = Field(..., description="Message timestamp")

class ChatMessageResponse(BaseModel):
    user_message: MessageResponse
    ai_response: MessageResponse

class ChatHistoryResponse(BaseModel):
    chat_id: int = Field(..., description="Chat session ID", example=1)
    messages: List[MessageResponse] = Field(..., description="Chat message history")

class ChatSummaryResponse(BaseModel):
    chat_id: int = Field(..., description="Chat session ID", example=1)
    persona: PersonaResponse
    last_message: Optional[str] = Field(None, description="Last message in chat", example="Hello Einstein!")
    message_count: int = Field(..., description="Total messages in chat", example=5)
    created_at: datetime = Field(..., description="Chat creation time")
    last_activity: Optional[datetime] = Field(None, description="Last message timestamp")

class UserChatsResponse(BaseModel):
    chats: List[ChatSummaryResponse] = Field(..., description="User's chat sessions")

class ChatDeleteResponse(BaseModel):
    message: str = Field(..., description="Delete confirmation", example="Chat deleted successfully")
    chat_id: int = Field(..., description="Deleted chat session ID", example=1)
    deleted: bool = Field(..., description="Deletion status", example=True)

# Error Response Models
class ErrorResponse(BaseModel):
    error: bool = Field(True, description="Error flag")
    message: str = Field(..., description="Error message", example="Invalid email or password")
    status_code: int = Field(..., description="HTTP status code", example=400)
    path: str = Field(..., description="Request path", example="/auth/login")
    help: str = Field(..., description="Help message", example="Check API documentation at /docs")

class ValidationErrorDetail(BaseModel):
    loc: List[str] = Field(..., description="Error location", example=["body", "email"])
    msg: str = Field(..., description="Error message", example="field required")
    type: str = Field(..., description="Error type", example="value_error.missing")

class ValidationErrorResponse(BaseModel):
    detail: List[ValidationErrorDetail] = Field(..., description="Validation error details")

# Google OAuth Models
class GoogleAuthRequest(BaseModel):
    credential: str = Field(..., description="Google ID token from frontend", example="eyJhbGciOiJSUzI1NiIs...")

class GoogleAuthResponse(BaseModel):
    message: str = Field(..., description="Authentication result", example="Google login successful")
    access_token: str = Field(..., description="JWT access token", example="eyJhbGciOiJIUzI1NiIs...")
    token_type: str = Field(..., description="Token type", example="bearer")
    user: 'UserResponse'
    is_new_user: bool = Field(..., description="Whether this is a new user registration", example=False)