# Wise Words – Conversational AI with Historical Figures

**Last Updated:** 2025-05-25

## 📌 Overview

**Wise Words** is a web-based conversational AI platform where users can chat with historically significant figures (e.g., Einstein, Newton, Elon Musk) through simulated natural dialogue. The goal is to provide an educational, engaging, and lifelike interaction experience, combining modern AI capabilities with curated historical data.

---

## 💡 Core Features

- User authentication (signup, login, profile)
- Persona selection from curated list of historical figures
- Real-time chat with AI that mimics each persona’s style and knowledge
- Chat history saved and accessible by the user
- Minimalist, responsive frontend for seamless UX

---

## 🧠 AI System

### Original:
- Used **OpenAI GPT-4 API**

### Now:
- Switched to **Google Gemini Pro API** (`gemini-pro`) for generating AI responses.

### AI Response Logic:
- Prompts are system-defined per persona (sourced from speeches, writings, etc.)
- Messages are passed with system prompt and chat history for coherent, character-consistent responses

---

## 🏗️ Tech Stack

| Layer        | Toolset                                   |
|--------------|-------------------------------------------|
| Frontend     | Next.js + Tailwind CSS + Shadcn/UI        |
| Backend      | FastAPI                                   |
| Database     | PostgreSQL (Hosted on Supabase)           |
| ORM/DB Layer | SQLAlchemy                                |
| AI Provider  | Gemini Pro API (via `google-generativeai`)|
| Dev Tools    | VS Code, Postman, .env, Uvicorn           |

---

## 🗃️ Database Schema (Simplified)

- **users**: id, email, nickname, password (hashed)
- **personas**: id, name, description, prompt
- **chats**: id, user_id, persona_id, created_at
- **messages**: id, chat_id, sender (user/ai), content, timestamp

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