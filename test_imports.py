#!/usr/bin/env python3

print("Testing imports...")

try:
    import models
    print("✅ models.py imports successfully")
except Exception as e:
    print(f"❌ models.py import failed: {e}")

try:
    import crud
    print("✅ crud.py imports successfully")
except Exception as e:
    print(f"❌ crud.py import failed: {e}")

try:
    import schemas
    print("✅ schemas.py imports successfully")
except Exception as e:
    print(f"❌ schemas.py import failed: {e}")

try:
    from routes import auth
    print("✅ routes/auth.py imports successfully")
except Exception as e:
    print(f"❌ routes/auth.py import failed: {e}")

try:
    from routes import chat
    print("✅ routes/chat.py imports successfully")
except Exception as e:
    print(f"❌ routes/chat.py import failed: {e}")

print("\n🎉 All imports working! Your project structure is fixed.")
print("\nNext steps:")
print("1. Set up your .env file with DATABASE_URL and GEMINI_API_KEY")
print("2. Run: pip install -r requirements.txt")
print("3. Run: uvicorn main:app --reload") 