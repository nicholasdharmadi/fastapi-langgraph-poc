#!/usr/bin/env python3
"""
Database migration script to add conversation_messages table.
Run this after updating the code to enable conversation tracking.
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import text
from app.database import engine
from app.config import settings

def run_migration():
    """Run the conversation_messages table migration."""
    
    migration_sql = """
    -- Create conversation_messages table
    CREATE TABLE IF NOT EXISTS conversation_messages (
        id SERIAL PRIMARY KEY,
        campaign_lead_id INTEGER NOT NULL REFERENCES campaign_leads(id) ON DELETE CASCADE,
        role VARCHAR(50) NOT NULL,
        content TEXT NOT NULL,
        metadata JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Create indexes
    CREATE INDEX IF NOT EXISTS idx_conversation_messages_campaign_lead_id 
    ON conversation_messages(campaign_lead_id);

    CREATE INDEX IF NOT EXISTS idx_conversation_messages_created_at 
    ON conversation_messages(created_at DESC);

    -- Add comments
    COMMENT ON TABLE conversation_messages IS 'Stores conversation history between AI agents and leads';
    COMMENT ON COLUMN conversation_messages.role IS 'Message role: system, assistant, user, or tool';
    COMMENT ON COLUMN conversation_messages.metadata IS 'Additional context like node name, step info, etc.';
    """
    
    print("🔄 Running conversation_messages migration...")
    print(f"📊 Database: {settings.DATABASE_URL.split('@')[-1]}")
    
    try:
        with engine.connect() as conn:
            # Execute migration
            conn.execute(text(migration_sql))
            conn.commit()
            
            # Verify table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'conversation_messages'
                );
            """))
            exists = result.scalar()
            
            if exists:
                print("✅ Migration completed successfully!")
                print("✅ conversation_messages table created")
                print("✅ Indexes created")
                
                # Check if there are any existing campaign_leads
                result = conn.execute(text("SELECT COUNT(*) FROM campaign_leads;"))
                count = result.scalar()
                print(f"📈 Found {count} existing campaign leads")
                
            else:
                print("❌ Migration failed - table not found")
                return False
                
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("LangSmith Integration - Database Migration")
    print("=" * 60)
    print()
    
    success = run_migration()
    
    print()
    if success:
        print("🎉 Migration complete! You can now:")
        print("   1. Configure LangSmith in your .env file")
        print("   2. Restart your backend and worker")
        print("   3. Run campaigns with conversation tracking")
        print()
        print("📚 See LANGSMITH_IMPLEMENTATION.md for details")
    else:
        print("⚠️  Migration failed. Please check the error above.")
        sys.exit(1)
