"""Workflow API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.workflow import Workflow
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate, WorkflowResponse

router = APIRouter(prefix="/workflows", tags=["workflows"])

@router.get("", response_model=List[WorkflowResponse])
@router.get("/", response_model=List[WorkflowResponse])
def list_workflows(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all workflows."""
    workflows = db.query(Workflow).offset(skip).limit(limit).all()
    return workflows

@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    """Get a specific workflow."""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@router.post("", response_model=WorkflowResponse, status_code=201)
@router.post("/", response_model=WorkflowResponse, status_code=201)
def create_workflow(workflow_data: WorkflowCreate, db: Session = Depends(get_db)):
    """Create a new workflow."""
    workflow = Workflow(**workflow_data.model_dump())
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return workflow

@router.put("/{workflow_id}", response_model=WorkflowResponse)
def update_workflow(workflow_id: int, workflow_data: WorkflowUpdate, db: Session = Depends(get_db)):
    """Update a workflow."""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    update_data = workflow_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workflow, field, value)
    
    db.commit()
    db.refresh(workflow)
    return workflow

@router.delete("/{workflow_id}", status_code=204)
def delete_workflow(workflow_id: int, db: Session = Depends(get_db)):
    """Delete a workflow."""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    db.delete(workflow)
    db.commit()
    return None
