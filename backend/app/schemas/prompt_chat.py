from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatSessionCreate(BaseModel):
    initial_message: Optional[str] = None

class ChatSessionResponse(BaseModel):
    id: int
    messages: List[ChatMessage]
    is_completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ChatMessageCreate(BaseModel):
    content: str

class ChatMessageResponse(BaseModel):
    role: str
    content: str
    draft_prompt: Optional[str] = None

class SavePromptRequest(BaseModel):
    name: Optional[str] = None
    draft_prompt: str
