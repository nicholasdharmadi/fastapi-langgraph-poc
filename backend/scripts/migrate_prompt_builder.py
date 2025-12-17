"""Migration script to create prompt builder tables."""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, engine
from app.models.recording import Recording, Transcript, Analysis, GeneratedPrompt, PromptChatSession

def migrate():
    """Create prompt builder tables."""
    print("Creating prompt builder tables...")
    
    # Drop existing tables if they exist (to handle column renames)
    print("Dropping existing tables if they exist...")
    GeneratedPrompt.__table__.drop(engine, checkfirst=True)
    PromptChatSession.__table__.drop(engine, checkfirst=True)
    Analysis.__table__.drop(engine, checkfirst=True)
    Transcript.__table__.drop(engine, checkfirst=True)
    Recording.__table__.drop(engine, checkfirst=True)
    
    # Create tables with new schema
    print("Creating new tables...")
    Base.metadata.create_all(bind=engine, tables=[
        Recording.__table__,
        Transcript.__table__,
        Analysis.__table__,
        PromptChatSession.__table__,
        GeneratedPrompt.__table__
    ])
    
    print("✓ Prompt builder tables created successfully!")

if __name__ == "__main__":
    migrate()
