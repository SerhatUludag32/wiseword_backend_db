# Wise Words – Conversational AI with Historical Figures

**Last Updated:** 2025-01-27

## 📌 Overview

**Wise Words** is a web-based conversational AI platform where users can chat with historically significant figures (e.g., Einstein, Newton, Elon Musk) through simulated natural dialogue. The goal is to provide an educational, engaging, and lifelike interaction experience, combining modern AI capabilities with curated historical data.

---

## 💡 Core Features

- User authentication (signup, login, profile)
- Persona selection from curated list of historical figures
- Real-time chat with AI that mimics each persona's style and knowledge
- Chat history saved and accessible by the user
- Minimalist, responsive frontend for seamless UX
- **🔐 Advanced prompt injection protection** - Characters stay in role even when users try to break them

---

## 🔐 Security Features

**Prompt Injection Protection**: Our system prevents users from breaking character roleplay through malicious prompts.

- **Multi-layer detection**: 13+ pattern-based injection detectors
- **Input sanitization**: Removes dangerous system markers and limits
- **Enhanced prompts**: Role-reinforced persona instructions
- **Automatic responses**: Character-appropriate redirects for injection attempts

**Test Results**: 100% detection rate on injection attempts, 0% false positives

📖 **Full Documentation**: See [PROMPT_SECURITY_GUIDE.md](PROMPT_SECURITY_GUIDE.md)

---

## 🧠 AI System

### Original:
- Used **OpenAI GPT-4 API**

### Now:
- Switched to **Google Gemini Pro API** (`gemini-pro`) for generating AI responses.

### AI Response Logic:
- Prompts are system-defined per persona (sourced from speeches, writings, etc.)
- Messages are passed with system prompt and chat history for coherent, character-consistent responses
- **Security layer** prevents prompt injection and maintains character integrity

---

## 🏗️ Tech Stack

| Layer        | Toolset                                   |
|--------------|-------------------------------------------|
| Frontend     | Next.js + Tailwind CSS + Shadcn/UI        |
| Backend      | FastAPI                                   |
| Database     | PostgreSQL (Hosted on Supabase)           |
| ORM/DB Layer | SQLAlchemy                                |
| AI Provider  | Gemini Pro API (via `google-generativeai`)|
| Security     | Custom prompt injection protection        |
| Dev Tools    | VS Code, Postman, .env, Uvicorn           |

---

## 🗃️ Database Schema (Simplified)

- **users**: id, email, nickname, password (hashed)
- **personas**: id, name, description, prompt
- **chats**: id, user_id, persona_id, created_at
- **messages**: id, chat_id, sender (user/ai), content, timestamp

---

## 🔧 Testing

### Security Testing
```bash
python test_prompt_security.py
```

### API Testing
Use the included Postman collection or test endpoints manually.

---

## 🧪 Early Design Process

- Created **paper prototypes** for login, discovery, chat, and profile screens
- Used feedback to finalize flow and interface layout
- Prioritized accessibility and historical immersion

---

## 🌐 Environment Configuration (.env)

```env
DATABASE_URL=postgresql://postgres:<password>@db.<project>.supabase.co:5432/postgres
GEMINI_API_KEY=your-gemini-key