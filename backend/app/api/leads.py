"""Lead API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Lead
from app.schemas import LeadCreate, LeadUpdate, LeadResponse

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("", response_model=List[LeadResponse])
@router.get("/", response_model=List[LeadResponse])
def list_leads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all leads."""
    leads = db.query(Lead).offset(skip).limit(limit).all()
    return leads


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    """Get a specific lead."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.post("", response_model=LeadResponse, status_code=201)
@router.post("/", response_model=LeadResponse, status_code=201)
def create_lead(lead_data: LeadCreate, db: Session = Depends(get_db)):
    """Create a new lead."""
    lead = Lead(**lead_data.model_dump())
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


@router.put("/{lead_id}", response_model=LeadResponse)
def update_lead(lead_id: int, lead_data: LeadUpdate, db: Session = Depends(get_db)):
    """Update a lead."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    update_data = lead_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)
    
    db.commit()
    db.refresh(lead)
    return lead


@router.delete("/{lead_id}", status_code=204)
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    """Delete a lead."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    db.delete(lead)
    db.commit()
    return None


@router.post("/upload", status_code=201)
async def upload_leads(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload leads from a CSV file.
    Expected columns: name, phone, email (optional), company (optional), notes (optional)
    """
    import csv
    import codecs
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    leads_created = 0
    errors = []
    
    try:
        # Read file content
        content = await file.read()
        decoded_content = content.decode('utf-8')
        csv_reader = csv.DictReader(codecs.iterdecode(content.splitlines(), 'utf-8'))
        
        # Reset file position if needed or just use the decoded content
        # Using StringIO to parse the decoded string
        from io import StringIO
        csv_file = StringIO(decoded_content)
        reader = csv.DictReader(csv_file)
        
        # Normalize headers (strip whitespace, lowercase)
        if reader.fieldnames:
            reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]
            
        required_fields = ['name', 'phone']
        
        for row in reader:
            # Skip empty rows
            if not any(row.values()):
                continue
                
            # Check required fields
            if not all(field in row for field in required_fields):
                errors.append(f"Row missing required fields: {row}")
                continue
                
            try:
                lead_data = LeadCreate(
                    name=row.get('name'),
                    phone=row.get('phone'),
                    email=row.get('email'),
                    company=row.get('company'),
                    notes=row.get('notes')
                )
                
                # Check if lead exists (by phone)
                existing_lead = db.query(Lead).filter(Lead.phone == lead_data.phone).first()
                if existing_lead:
                    # Update existing? Or skip? Let's skip for now or update if needed.
                    # User didn't specify, but usually we might want to update or skip.
                    # Let's just log it and skip to avoid duplicates for now.
                    continue
                
                lead = Lead(**lead_data.model_dump())
                db.add(lead)
                leads_created += 1
                
            except Exception as e:
                errors.append(f"Error processing row {row}: {str(e)}")
        
        db.commit()
        
        return {
            "message": f"Successfully imported {leads_created} leads",
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")
