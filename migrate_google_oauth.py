"""
Migration script to add Google OAuth fields to existing User table
Run this once after updating the models.py file
"""

from sqlalchemy import text
from database import engine
import logging

def migrate_database():
    """Add Google OAuth columns to existing users table"""
    
    migration_queries = [
        # Add google_id column
        """
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS google_id VARCHAR UNIQUE;
        """,
        
        # Add auth_provider column with default value
        """
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS auth_provider VARCHAR DEFAULT 'email';
        """,
        
        # Add profile_picture column
        """
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS profile_picture VARCHAR;
        """,
        
        # Make hashed_password nullable for Google OAuth users
        """
        ALTER TABLE users 
        ALTER COLUMN hashed_password DROP NOT NULL;
        """,
        
        # Update existing users to have 'email' as auth_provider
        """
        UPDATE users 
        SET auth_provider = 'email' 
        WHERE auth_provider IS NULL;
        """
    ]
    
    try:
        with engine.connect() as connection:
            for query in migration_queries:
                print(f"Executing: {query.strip()}")
                connection.execute(text(query))
                connection.commit()
                print("✅ Success")
        
        print("\n🎉 Database migration completed successfully!")
        print("Google OAuth fields have been added to the users table.")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("Please check your database connection and try again.")

if __name__ == "__main__":
    print("🔄 Starting Google OAuth database migration...")
    migrate_database() 