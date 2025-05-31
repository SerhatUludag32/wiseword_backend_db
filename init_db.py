#!/usr/bin/env python3
"""
Database Initialization Script
Run this script once to create all database tables.
"""

from database import engine, Base
from models import User, Persona, Chat, Message
import sys

def init_database():
    """Initialize database by creating all tables."""
    try:
        print("🔄 Initializing database...")
        print(f"📊 Creating tables for: {', '.join([User.__tablename__, Persona.__tablename__, Chat.__tablename__, Message.__tablename__])}")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database initialization completed successfully!")
        print("🎯 Tables created:")
        print("   • users")
        print("   • personas") 
        print("   • chats")
        print("   • messages")
        print("\n💡 You can now check your Neon Dashboard → 'Tables' to confirm the tables were created.")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database() 