"""
Migration script to update agent role enum values to uppercase.
"""
from sqlalchemy import create_engine, text
from app.config import settings

def migrate():
    print("Starting agent role enum migration...")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.begin() as conn:
        try:
            # Update existing lowercase values to uppercase
            print("Updating agent roles to uppercase...")
            
            conn.execute(text("""
                UPDATE agents 
                SET role = 'HYBRID' 
                WHERE role = 'hybrid';
            """))
            
            conn.execute(text("""
                UPDATE agents 
                SET role = 'CREATIVE' 
                WHERE role = 'creative';
            """))
            
            conn.execute(text("""
                UPDATE agents 
                SET role = 'DETERMINISTIC' 
                WHERE role = 'deterministic';
            """))
            
            print("Agent roles updated successfully!")
            conn.commit()
            
        except Exception as e:
            print(f"Error during migration: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    migrate()
