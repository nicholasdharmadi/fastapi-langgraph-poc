"""State definitions for LangGraph workflows."""
from typing import TypedDict, List, Dict, Any, Annotated
import operator


class CampaignLeadState(TypedDict):
    """State for processing a single campaign lead."""
    
    # Identifiers
    campaign_lead_id: str
    campaign_id: str
    lead_id: str
    
    # Lead data
    lead_data: Dict[str, Any]  # name, phone, email, etc.
    
    # Campaign configuration
    agent_type: str  # 'sms', 'voice', or 'both'
    
    # A2A Architecture: Dual agent configuration
    use_a2a: bool  # Whether to use agent-to-agent architecture
    creative_agent_id: str  # ID of creative agent
    creative_agent_prompt: str  # System prompt for creative agent
    creative_agent_model: str  # Model for creative agent
    deterministic_agent_id: str  # ID of deterministic agent
    deterministic_agent_prompt: str  # System prompt for deterministic agent
    deterministic_agent_model: str  # Model for deterministic agent
    deterministic_agent_tools: List[Dict[str, Any]]  # Tools available to deterministic agent
    
    # Legacy single agent (for backward compatibility)
    sms_system_prompt: str
    sms_temperature: float
    
    # Processing results
    validation_passed: bool
    validation_errors: Annotated[List[str], operator.add]
    
    sms_sent: bool
    sms_message: str
    sms_error: str
    sms_cost: float  # Cost in USD
    
    voice_call_made: bool
    voice_call_id: str
    voice_error: str
    voice_cost: float  # Cost in USD
    
    # Enrichment results
    enrichment_data: Dict[str, Any]
    enrichment_error: str
    
    # Metadata
    processing_logs: Annotated[List[Dict[str, Any]], operator.add]
    conversation_history: Annotated[List[Dict[str, Any]], operator.add]  # Track all messages
    trace_id: str
    
    # Status
    status: str  # 'pending', 'processing', 'completed', 'failed'
    error_message: str

