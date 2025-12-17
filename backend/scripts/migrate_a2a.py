"""
Database migration script for A2A (Agent-to-Agent) architecture.

This script adds:
1. role column to agents table
2. creative_agent_id and deterministic_agent_id columns to campaigns table
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import text
from app.database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_a2a_schema():
    """Apply A2A schema migrations."""
    
    with engine.connect() as conn:
        try:
            # Start transaction
            trans = conn.begin()
            
            # 1. Add role column to agents table
            logger.info("Adding 'role' column to agents table...")
            conn.execute(text("""
                ALTER TABLE agents 
                ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'hybrid'
            """))
            
            # Update existing agents to 'hybrid' role
            conn.execute(text("""
                UPDATE agents 
                SET role = 'hybrid' 
                WHERE role IS NULL
            """))
            
            logger.info("✓ Added 'role' column to agents table")
            
            # 2. Add creative_agent_id to campaigns table
            logger.info("Adding 'creative_agent_id' column to campaigns table...")
            conn.execute(text("""
                ALTER TABLE campaigns 
                ADD COLUMN IF NOT EXISTS creative_agent_id INTEGER REFERENCES agents(id)
            """))
            
            logger.info("✓ Added 'creative_agent_id' column to campaigns table")
            
            # 3. Add deterministic_agent_id to campaigns table
            logger.info("Adding 'deterministic_agent_id' column to campaigns table...")
            conn.execute(text("""
                ALTER TABLE campaigns 
                ADD COLUMN IF NOT EXISTS deterministic_agent_id INTEGER REFERENCES agents(id)
            """))
            
            logger.info("✓ Added 'deterministic_agent_id' column to campaigns table")
            
            # Commit transaction
            trans.commit()
            logger.info("✅ A2A migration completed successfully!")
            
        except Exception as e:
            trans.rollback()
            logger.error(f"❌ Migration failed: {str(e)}")
            raise


def seed_a2a_agents():
    """Seed example A2A agents."""
    
    from app.database import SessionLocal
    from app.models import Agent, AgentRole
    
    db = SessionLocal()
    
    try:
        # Check if A2A agents already exist
        existing_creative = db.query(Agent).filter(Agent.role == AgentRole.CREATIVE).first()
        existing_deterministic = db.query(Agent).filter(Agent.role == AgentRole.DETERMINISTIC).first()
        
        if existing_creative and existing_deterministic:
            logger.info("A2A agents already exist, skipping seed")
            return
        
        # Create creative agent
        if not existing_creative:
            creative_agent = Agent(
                name="Creative Sales Agent",
                description="Specialized in crafting engaging, personalized sales messages",
                system_prompt="""You are a creative sales assistant focused on engaging conversation.
Your role is to:
- Craft personalized, compelling messages
- Maintain a friendly, professional tone
- Adapt messaging based on lead context
- Keep messages concise and action-oriented

Generate messages that feel human and authentic, not robotic.""",
                model="gpt-4o",
                role=AgentRole.CREATIVE,
                capabilities=["sms", "email"],
                tools=[]
            )
            db.add(creative_agent)
            logger.info("✓ Created creative agent")
        
        # Create deterministic agent
        if not existing_deterministic:
            deterministic_agent = Agent(
                name="Execution Agent",
                description="Handles tool execution, API calls, and structured operations",
                system_prompt="""You are a deterministic assistant focused on executing tools and actions.
Your role is to:
- Execute tool calls accurately
- Handle API integrations
- Manage structured data operations
- Ensure reliable delivery of messages

You work in tandem with the creative agent to execute their plans.""",
                model="gpt-4o-mini",
                role=AgentRole.DETERMINISTIC,
                capabilities=["sms", "voice", "api"],
                tools=[
                    {"name": "send_sms", "config": {"provider": "twilio"}},
                    {"name": "make_call", "config": {"provider": "livekit"}},
                ]
            )
            db.add(deterministic_agent)
            logger.info("✓ Created deterministic agent")
        
        db.commit()
        logger.info("✅ A2A agents seeded successfully!")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Seeding failed: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Starting A2A migration...")
    migrate_a2a_schema()
    logger.info("\nSeeding A2A agents...")
    seed_a2a_agents()
    logger.info("\n✅ All A2A setup completed!")
