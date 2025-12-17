"""Seed database with sample data."""
import logging
from app.database import SessionLocal
from app.models import Lead

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_leads():
    """Create sample leads."""
    db = SessionLocal()
    
    try:
        # Check if leads already exist
        existing_count = db.query(Lead).count()
        if existing_count > 0:
            logger.info(f"Database already has {existing_count} leads. Skipping seed.")
            return
        
        sample_leads = [
            {"name": "John Doe", "phone": "+1234567890", "email": "john@example.com", "company": "Acme Corp"},
            {"name": "Jane Smith", "phone": "+1234567891", "email": "jane@example.com", "company": "Tech Inc"},
            {"name": "Bob Johnson", "phone": "+1234567892", "email": "bob@example.com", "company": "StartupXYZ"},
            {"name": "Alice Williams", "phone": "+1234567893", "email": "alice@example.com", "company": "BigCo"},
            {"name": "Charlie Brown", "phone": "+1234567894", "email": "charlie@example.com", "company": "SmallBiz"},
            {"name": "Diana Prince", "phone": "+1234567895", "email": "diana@example.com", "company": "Enterprise Ltd"},
            {"name": "Eve Davis", "phone": "+1234567896", "email": "eve@example.com", "company": "Global Inc"},
            {"name": "Frank Miller", "phone": "+1234567897", "email": "frank@example.com", "company": "Local Shop"},
            {"name": "Grace Lee", "phone": "+1234567898", "email": "grace@example.com", "company": "Tech Startup"},
            {"name": "Henry Wilson", "phone": "+1234567899", "email": "henry@example.com", "company": "Consulting Co"},
        ]
        
        for lead_data in sample_leads:
            lead = Lead(**lead_data)
            db.add(lead)
        
        db.commit()
        logger.info(f"Created {len(sample_leads)} sample leads")
        
    except Exception as e:
        logger.error(f"Error seeding data: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Seeding database...")
    seed_leads()
    logger.info("Done!")

