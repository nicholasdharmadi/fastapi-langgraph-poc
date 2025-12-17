#!/usr/bin/env python3
"""Non-interactive script to add sample leads."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models import Lead

# Sample lead data
SAMPLE_LEADS = [
    {"name": "John Smith", "phone": "+1234567890", "email": "john@example.com", "company": "Acme Corp"},
    {"name": "Jane Doe", "phone": "+1234567891", "email": "jane@example.com", "company": "Tech Inc"},
    {"name": "Bob Johnson", "phone": "+1234567892", "email": "bob@example.com", "company": "StartupXYZ"},
    {"name": "Alice Williams", "phone": "+1234567893", "email": "alice@example.com", "company": "BigCo"},
    {"name": "Charlie Brown", "phone": "+1234567894", "email": "charlie@example.com", "company": "SmallBiz"},
    {"name": "Diana Prince", "phone": "+1234567895", "email": "diana@example.com", "company": "Enterprise LLC"},
    {"name": "Eve Adams", "phone": "+1234567896", "email": "eve@example.com", "company": "Growth Co"},
    {"name": "Frank Miller", "phone": "+1234567897", "email": "frank@example.com", "company": "Innovation Labs"},
    {"name": "Grace Lee", "phone": "+1234567898", "email": "grace@example.com", "company": "Future Tech"},
    {"name": "Henry Davis", "phone": "+1234567899", "email": "henry@example.com", "company": "Digital Solutions"},
    {"name": "Ivy Chen", "phone": "+1234567800", "email": "ivy@example.com", "company": "Cloud Systems"},
    {"name": "Jack Wilson", "phone": "+1234567801", "email": "jack@example.com", "company": "Data Corp"},
    {"name": "Kate Martinez", "phone": "+1234567802", "email": "kate@example.com", "company": "AI Ventures"},
    {"name": "Leo Garcia", "phone": "+1234567803", "email": "leo@example.com", "company": "Mobile First"},
    {"name": "Mia Rodriguez", "phone": "+1234567804", "email": "mia@example.com", "company": "Web Services"},
    {"name": "Noah Anderson", "phone": "+1234567805", "email": "noah@example.com", "company": "Platform Inc"},
    {"name": "Olivia Taylor", "phone": "+1234567806", "email": "olivia@example.com", "company": "SaaS Company"},
    {"name": "Paul Thomas", "phone": "+1234567807", "email": "paul@example.com", "company": "API Solutions"},
    {"name": "Quinn Moore", "phone": "+1234567808", "email": "quinn@example.com", "company": "DevOps Pro"},
    {"name": "Rachel Jackson", "phone": "+1234567809", "email": "rachel@example.com", "company": "Security Plus"},
]


def main():
    """Create sample leads (non-interactive)."""
    db = SessionLocal()
    
    try:
        print("🌱 Adding sample leads...")
        
        # Check if leads already exist
        existing_count = db.query(Lead).count()
        if existing_count > 0:
            print(f"   Found {existing_count} existing leads")
            print("   Adding new leads to existing ones...")
        
        # Create new leads (skip duplicates by phone)
        created = 0
        skipped = 0
        existing_phones = {lead.phone for lead in db.query(Lead.phone).all()}
        
        for lead_data in SAMPLE_LEADS:
            if lead_data["phone"] in existing_phones:
                skipped += 1
                continue
            lead = Lead(**lead_data)
            db.add(lead)
            created += 1
        
        db.commit()
        print(f"✅ Created {created} new leads")
        if skipped > 0:
            print(f"   Skipped {skipped} duplicate leads")
        
        # Show summary
        total = db.query(Lead).count()
        print(f"\n📊 Total leads in database: {total}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()



