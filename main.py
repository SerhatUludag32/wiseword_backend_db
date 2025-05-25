from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routes import auth, chat
from database import engine
from models import Base
import logging

# Create database tables
Base.metadata.create_all(bind=engine)

# Enhanced API documentation
app = FastAPI(
    title="🧠 Wise Words API",
    description="""
    ## Chat with Historical Figures AI Backend
    
    A conversational AI system that lets you chat with history's greatest minds:
    - 🧠 **Albert Einstein** - Physics, relativity, quantum mechanics
    - 🍎 **Isaac Newton** - Mathematics, gravity, classical mechanics  
    - 🎨 **Leonardo da Vinci** - Art, inventions, Renaissance genius
    - ⚛️ **Marie Curie** - Chemistry, radioactivity, women in science
    
    ### Features:
    - ✅ **Code-based email verification** (6-digit codes)
    - ✅ **JWT authentication** with secure tokens
    - ✅ **Real-time streaming responses** (like ChatGPT)
    - ✅ **Persistent chat history** with PostgreSQL
    - ✅ **Production-ready** deployment on Railway
    
    ### Quick Start:
    1. **Register** → Get verification code via email
    2. **Verify** → Enter 6-digit code  
    3. **Login** → Get JWT token
    4. **Authorize** → Click 🔒 button, paste: `Bearer your_token`
    5. **Chat** → Start conversation with any historical figure
    
    ### Frontend Integration:
    - Use `/auth/register` → `/auth/verify-code` → `/auth/login` flow
    - For real-time responses: use `/chat/message/stream` 
    - For simple responses: use `/chat/message`
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Wise Words API",
        "email": "support@wisewords.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }
)

# Global Exception Handler for Better Error Messages
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path),
            "help": "Check API documentation at /docs for proper usage"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error. Please try again later.",
            "status_code": 500,
            "path": str(request.url.path),
            "help": "If this persists, contact support"
        }
    )

# CORS Configuration for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with actual frontend URLs in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers with detailed tags
app.include_router(
    auth.router, 
    prefix="/auth", 
    tags=["🔐 Authentication"],
    responses={
        400: {"description": "Bad Request - Invalid input data"},
        401: {"description": "Unauthorized - Invalid credentials"},
        404: {"description": "Not Found - User/resource not found"},
        500: {"description": "Internal Server Error"}
    }
)

app.include_router(
    chat.router, 
    prefix="/chat", 
    tags=["💬 Chat with Historical Figures"],
    responses={
        200: {"description": "Success"},
        400: {"description": "Bad Request - Invalid chat data"},
        401: {"description": "Unauthorized - Login required"},
        404: {"description": "Not Found - Chat/persona not found"},
        500: {"description": "Internal Server Error"}
    }
)

@app.get(
    "/", 
    summary="🏠 API Health Check", 
    description="Check if the Wise Words API is running and get basic information",
    response_description="API status and helpful links"
)
def read_root():
    return {
        "status": "✅ Online",
        "message": "🧠 Wise Words API - Chat with Historical Figures",
        "version": "2.0.0",
        "documentation": "/docs",
        "alternative_docs": "/redoc",
        "features": [
            "Code-based email verification",
            "JWT authentication", 
            "Real-time streaming chat",
            "4 historical personalities",
            "Production-ready deployment"
        ],
        "quick_start": {
            "1": "POST /auth/register - Create account",
            "2": "POST /auth/verify-code - Verify email", 
            "3": "POST /auth/login - Get JWT token",
            "4": "Click 🔒 Authorize in /docs",
            "5": "POST /chat/start - Begin conversation"
        }
    }