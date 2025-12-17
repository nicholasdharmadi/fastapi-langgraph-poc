"""
Migration script to add manual_mode column to campaign_leads table.
"""
from sqlalchemy import create_engine, text
from app.config import settings

def migrate():
    print("Starting manual_mode migration...")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.begin() as conn:
        try:
            # Check if column exists first
            print("Checking if manual_mode column exists...")
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='campaign_leads' AND column_name='manual_mode';
            """))
            
            if not result.fetchone():
                print("Adding manual_mode column to campaign_leads table...")
                conn.execute(text("""
                    ALTER TABLE campaign_leads 
                    ADD COLUMN manual_mode BOOLEAN DEFAULT FALSE;
                """))
                print("Column manual_mode added.")
                conn.commit()
            else:
                print("Column manual_mode already exists.")
                
            print("Migration completed successfully!")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    migrate()
