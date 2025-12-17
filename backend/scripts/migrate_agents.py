"""
Migration script to create agents table and add agent_id to campaigns.
"""
import os
import sys
from sqlalchemy import create_engine, text
from app.config import settings

def migrate():
    print("Starting migration...")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.begin() as conn:
        try:
            # Create agents table
            print("Creating agents table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS agents (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    system_prompt TEXT NOT NULL,
                    model VARCHAR(50) NOT NULL DEFAULT 'gpt-4o',
                    capabilities JSONB NOT NULL DEFAULT '[]',
                    tools JSONB NOT NULL DEFAULT '[]',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """))
            
            # Add agent_id to campaigns table
            print("Adding agent_id to campaigns table...")
            # Check if column exists first
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='campaigns' AND column_name='agent_id';
            """))
            
            if not result.fetchone():
                conn.execute(text("""
                    ALTER TABLE campaigns 
                    ADD COLUMN agent_id INTEGER REFERENCES agents(id);
                """))
                print("Column agent_id added.")
            else:
                print("Column agent_id already exists.")
                
            print("Migration completed successfully!")
            conn.commit()
            
        except Exception as e:
            print(f"Error during migration: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    migrate()
