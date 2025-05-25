import google.generativeai as genai
import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import SessionLocal
import crud, schemas, models
import jwt
import json

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")

router = APIRouter()
security = HTTPBearer()

SECRET_KEY = "your-secret-key-for-school-project"
ALGORITHM = "HS256"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if email is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def generate_ai_response_stream(messages: list, system_prompt: str):
    """Generator function that yields AI response chunks in real-time"""
    try:
        chat = model.start_chat(history=[])
        full_prompt = system_prompt + "\n\n" + "\n".join([f"{m['sender']}: {m['content']}" for m in messages])
        
        # Use streaming with Gemini API
        response = chat.send_message(full_prompt, stream=True)
        
        full_response = ""
        for chunk in response:
            if chunk.text:
                full_response += chunk.text
                # Yield chunk in SSE format for streaming
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk.text})}\n\n"
        
        # Yield the complete response for database saving
        yield f"data: {json.dumps({'type': 'complete', 'content': full_response})}\n\n"
        yield f"data: {json.dumps({'type': 'end'})}\n\n"
        
    except Exception as e:
        error_msg = "I apologize, but I'm having trouble responding right now. Please try again."
        yield f"data: {json.dumps({'type': 'complete', 'content': error_msg})}\n\n"
        yield f"data: {json.dumps({'type': 'end'})}\n\n"

def generate_ai_response(messages: list, system_prompt: str):
    try:
        chat = model.start_chat(history=[])
        full_prompt = system_prompt + "\n\n" + "\n".join([f"{m['sender']}: {m['content']}" for m in messages])
        response = chat.send_message(full_prompt)
        return response.text
    except Exception as e:
        return f"I apologize, but I'm having trouble responding right now. Please try again."

@router.get("/personas")
def get_personas(db: Session = Depends(get_db)):
    personas = crud.get_personas(db)
    return {"personas": personas}

@router.post("/start")
def start_chat(persona_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if persona exists
    persona = crud.get_persona_by_id(db, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    # Create new chat
    chat = crud.create_chat(db, current_user.id, persona_id)
    
    return {
        "message": "Chat started",
        "chat_id": chat.id,
        "persona": {"id": persona.id, "name": persona.name, "description": persona.description}
    }

@router.post("/message")
def send_message(message: schemas.MessageCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get chat and verify it belongs to user
    chat = db.query(models.Chat).filter(
        models.Chat.id == message.chat_id,
        models.Chat.user_id == current_user.id
    ).first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Save user message
    user_message = crud.create_message(db, message.chat_id, "user", message.content)
    
    # Get persona for AI response
    persona = crud.get_persona_by_id(db, chat.persona_id)
    
    # Get chat history for context
    chat_messages = crud.get_chat_messages(db, message.chat_id)
    message_history = [{"sender": msg.sender, "content": msg.content} for msg in chat_messages[:-1]]  # Exclude the just-added message
    
    # Generate AI response
    ai_response = generate_ai_response(message_history + [{"sender": "user", "content": message.content}], persona.prompt)
    
    # Save AI response
    ai_message = crud.create_message(db, message.chat_id, "ai", ai_response)
    
    return {
        "user_message": {"id": user_message.id, "content": user_message.content, "timestamp": user_message.timestamp},
        "ai_response": {"id": ai_message.id, "content": ai_message.content, "timestamp": ai_message.timestamp}
    }

@router.post("/message/stream")
def send_message_stream(message: schemas.MessageCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get chat and verify it belongs to user
    chat = db.query(models.Chat).filter(
        models.Chat.id == message.chat_id,
        models.Chat.user_id == current_user.id
    ).first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Save user message
    user_message = crud.create_message(db, message.chat_id, "user", message.content)
    
    # Get persona for AI response
    persona = crud.get_persona_by_id(db, chat.persona_id)
    
    # Get chat history for context
    chat_messages = crud.get_chat_messages(db, message.chat_id)
    message_history = [{"sender": msg.sender, "content": msg.content} for msg in chat_messages[:-1]]  # Exclude the just-added message
    
    def stream_with_db_save():
        full_ai_response = ""
        
        # Add initial response with user message info
        yield f"data: {json.dumps({'type': 'user_message', 'id': user_message.id, 'content': user_message.content, 'timestamp': str(user_message.timestamp)})}\n\n"
        
        # Stream AI response
        for chunk_data in generate_ai_response_stream(message_history + [{"sender": "user", "content": message.content}], persona.prompt):
            yield chunk_data
            
            # Parse chunk to get complete response for DB saving
            if chunk_data.startswith("data: "):
                try:
                    chunk_json = json.loads(chunk_data[6:])
                    if chunk_json.get('type') == 'complete':
                        full_ai_response = chunk_json.get('content', '')
                except:
                    pass
        
        # Save complete AI response to database
        if full_ai_response:
            ai_message = crud.create_message(db, message.chat_id, "ai", full_ai_response)
            yield f"data: {json.dumps({'type': 'ai_message_saved', 'id': ai_message.id, 'timestamp': str(ai_message.timestamp)})}\n\n"
    
    return StreamingResponse(
        stream_with_db_save(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

@router.get("/history/{chat_id}")
def get_chat_history(chat_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verify chat belongs to user
    chat = db.query(models.Chat).filter(
        models.Chat.id == chat_id,
        models.Chat.user_id == current_user.id
    ).first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    messages = crud.get_chat_messages(db, chat_id)
    
    return {
        "chat_id": chat_id,
        "messages": [{"id": msg.id, "sender": msg.sender, "content": msg.content, "timestamp": msg.timestamp} for msg in messages]
    }