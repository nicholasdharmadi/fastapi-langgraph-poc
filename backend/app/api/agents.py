"""Agent API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse

router = APIRouter(prefix="/agents", tags=["agents"])

@router.get("", response_model=List[AgentResponse])
@router.get("/", response_model=List[AgentResponse])
def list_agents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all agents."""
    agents = db.query(Agent).offset(skip).limit(limit).all()
    return agents

@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: int, db: Session = Depends(get_db)):
    """Get a specific agent."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.post("", response_model=AgentResponse, status_code=201)
@router.post("/", response_model=AgentResponse, status_code=201)
def create_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
    """Create a new agent."""
    agent = Agent(**agent_data.model_dump())
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent

@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(agent_id: int, agent_data: AgentUpdate, db: Session = Depends(get_db)):
    """Update an agent."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    update_data = agent_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)
    
    db.commit()
    db.refresh(agent)
    return agent

@router.delete("/{agent_id}", status_code=204)
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    """Delete an agent."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db.delete(agent)
    db.commit()
    return None
