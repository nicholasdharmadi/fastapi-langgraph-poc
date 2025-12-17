"""LangGraph workflow definition for campaign processing."""
import logging
import os
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session
from datetime import datetime
from app.orchestrator.state import CampaignLeadState
from app.orchestrator.nodes import (
    validate_lead_node,
    sms_agent_node,
    voice_agent_node,
    enrichment_node,
    finalize_node,
    route_after_validation,
    route_after_sms
)
from app.orchestrator.a2a_nodes import (
    a2a_creative_agent_node,
    a2a_deterministic_agent_node,
    a2a_handoff_node,
    route_a2a_workflow
)
from app.config import settings
from langsmith import Client
from langsmith.run_helpers import traceable

logger = logging.getLogger(__name__)


def create_campaign_lead_graph():
    """Create the LangGraph workflow for processing a single campaign lead."""
    
    workflow = StateGraph(CampaignLeadState)
    
    # Add nodes
    workflow.add_node("validate", validate_lead_node)
    workflow.add_node("sms_agent", sms_agent_node)
    workflow.add_node("voice_agent", voice_agent_node)
    workflow.add_node("finalize", finalize_node)
    
    # Set entry point
    workflow.set_entry_point("validate")
    
    # Add conditional edges after validation
    workflow.add_conditional_edges(
        "validate",
        route_after_validation,
        {
            "sms_only": "sms_agent",
            "voice_only": "voice_agent",
            "sms_first": "sms_agent",
            "finalize": "finalize"
        }
    )
    
    # Add conditional edges after SMS
    workflow.add_conditional_edges(
        "sms_agent",
        route_after_sms,
        {
            "voice": "voice_agent",
            "finalize": "finalize"
        }
    )
    
    # Voice agent always goes to finalize
    workflow.add_edge("voice_agent", "finalize")
    
    # Finalize is the end
    workflow.add_edge("finalize", END)
    
    # Compile the graph
    compiled_graph = workflow.compile()
    
    logger.info("Campaign lead graph compiled successfully")
    logger.info("Campaign lead graph compiled successfully")
    return compiled_graph


def create_a2a_campaign_lead_graph():
    """Create the LangGraph workflow for A2A (Agent-to-Agent) processing."""
    
    workflow = StateGraph(CampaignLeadState)
    
    # Add nodes
    workflow.add_node("validate", validate_lead_node)
    workflow.add_node("creative_agent", a2a_creative_agent_node)
    workflow.add_node("deterministic_agent", a2a_deterministic_agent_node)
    workflow.add_node("handoff", a2a_handoff_node)
    workflow.add_node("finalize", finalize_node)
    
    # Set entry point
    workflow.set_entry_point("validate")
    
    # After validation, route to creative agent or finalize
    workflow.add_conditional_edges(
        "validate",
        route_a2a_workflow,
        {
            "creative": "creative_agent",
            "finalize": "finalize"
        }
    )
    
    # After creative agent, go to handoff
    workflow.add_edge("creative_agent", "handoff")
    
    # After handoff, route to deterministic agent or finalize
    workflow.add_conditional_edges(
        "handoff",
        route_a2a_workflow,
        {
            "deterministic": "deterministic_agent",
            "finalize": "finalize"
        }
    )
    
    # After deterministic agent, finalize
    workflow.add_edge("deterministic_agent", "finalize")
    
    # Finalize is the end
    workflow.add_edge("finalize", END)
    
    # Compile the graph
    compiled_graph = workflow.compile()
    
    logger.info("A2A campaign lead graph compiled successfully")
    return compiled_graph


def create_dynamic_campaign_lead_graph(workflow_config: dict):
    """Create a dynamic LangGraph workflow based on configuration."""
    workflow = StateGraph(CampaignLeadState)
    
    nodes_config = workflow_config.get('nodes', [])
    edges_config = workflow_config.get('edges', [])
    
    # Map visual node types/labels to functions
    # In a real app, this would be more robust (e.g. by node type)
    # Here we use the label or id prefix to guess the node type
    
    node_mapping = {}  # visual_id -> graph_node_name
    
    for node in nodes_config:
        visual_id = node['id']
        label = node['data']['label'].lower()
        
        if 'start' in label or node.get('type') == 'input':
            # Start node is just a marker, we set entry point to its target
            continue
        elif 'end' in label or node.get('type') == 'output':
            workflow.add_node("finalize", finalize_node)
            node_mapping[visual_id] = "finalize"
        elif 'validate' in label:
            workflow.add_node("validate", validate_lead_node)
            node_mapping[visual_id] = "validate"
        elif 'sms' in label:
            workflow.add_node("sms_agent", sms_agent_node)
            node_mapping[visual_id] = "sms_agent"
        elif 'voice' in label:
            workflow.add_node("voice_agent", voice_agent_node)
            node_mapping[visual_id] = "voice_agent"
        elif 'enrich' in label:
            workflow.add_node("enrichment", enrichment_node)
            node_mapping[visual_id] = "enrichment"
        else:
            # Default or unknown -> pass through or log
            logger.warning(f"Unknown node type: {label}")
            
    # Add edges
    # We need to find the entry point (target of start node)
    entry_point = None
    
    for edge in edges_config:
        source_id = edge['source']
        target_id = edge['target']
        
        # Check if source is start node
        source_node = next((n for n in nodes_config if n['id'] == source_id), None)
        if source_node and (source_node.get('type') == 'input' or 'start' in source_node['data']['label'].lower()):
            if target_id in node_mapping:
                entry_point = node_mapping[target_id]
            continue
            
        if source_id in node_mapping and target_id in node_mapping:
            source_name = node_mapping[source_id]
            target_name = node_mapping[target_id]
            
            # Special handling for validation
            if source_name == "validate":
                workflow.add_conditional_edges(
                    "validate",
                    (lambda target: lambda state: target if state['validation_passed'] else "finalize")(target_name),
                    {
                        target_name: target_name,
                        "finalize": "finalize"
                    }
                )
            else:
                workflow.add_edge(source_name, target_name)
    
    if entry_point:
        workflow.set_entry_point(entry_point)
    else:
        # Fallback if no start node connected
        workflow.set_entry_point("validate")
        
    # Ensure finalize goes to END
    workflow.add_edge("finalize", END)
    
    return workflow.compile()


def initialize_lead_state(campaign_lead, campaign, lead) -> CampaignLeadState:
    """Initialize the state for processing a campaign lead."""
    return {
        # Identifiers
        'campaign_lead_id': str(campaign_lead.id),
        'campaign_id': str(campaign.id),
        'lead_id': str(lead.id),
        
        # Lead data
        'lead_data': {
            'name': lead.name,
            'phone': lead.phone,
            'email': lead.email or '',
            'company': lead.company or '',
            'notes': lead.notes or '',
        },
        
        # Campaign configuration
        'agent_type': campaign.agent_type.value,
        
        # A2A Architecture configuration
        'use_a2a': bool(campaign.creative_agent_id and campaign.deterministic_agent_id),
        'creative_agent_id': str(campaign.creative_agent_id) if campaign.creative_agent_id else '',
        'creative_agent_prompt': (
            campaign.creative_agent.system_prompt 
            if campaign.creative_agent_id and campaign.creative_agent 
            else "You are a creative sales assistant focused on engaging conversation."
        ),
        'creative_agent_model': (
            campaign.creative_agent.model 
            if campaign.creative_agent_id and campaign.creative_agent 
            else "gpt-4o"
        ),
        'deterministic_agent_id': str(campaign.deterministic_agent_id) if campaign.deterministic_agent_id else '',
        'deterministic_agent_prompt': (
            campaign.deterministic_agent.system_prompt 
            if campaign.deterministic_agent_id and campaign.deterministic_agent 
            else "You are a deterministic assistant focused on executing tools and actions."
        ),
        'deterministic_agent_model': (
            campaign.deterministic_agent.model 
            if campaign.deterministic_agent_id and campaign.deterministic_agent 
            else "gpt-4o"
        ),
        'deterministic_agent_tools': (
            campaign.deterministic_agent.tools 
            if campaign.deterministic_agent_id and campaign.deterministic_agent 
            else []
        ),
        
        # Legacy single agent (for backward compatibility)
        'sms_system_prompt': (
            campaign.agent.system_prompt 
            if campaign.agent_id and campaign.agent 
            else (campaign.sms_system_prompt or "You are a helpful sales assistant.")
        ),
        'sms_temperature': campaign.sms_temperature / 100.0,  # Convert 0-100 to 0.0-1.0,
        
        # Processing results (initialized)
        'validation_passed': False,
        'validation_errors': [],
        
        'sms_sent': False,
        'sms_message': '',
        'sms_error': '',
        'sms_cost': 0.0,
        
        'voice_call_made': False,
        'voice_call_id': '',
        'voice_error': '',
        'voice_cost': 0.0,
        
        # Enrichment results
        'enrichment_data': {},
        'enrichment_error': '',
        
        # Metadata
        'processing_logs': [],
        'conversation_history': [],
        'trace_id': '',
        
        # Status
        'status': 'pending',
        'error_message': '',
    }


def process_campaign_lead_with_graph(campaign_lead_id: int, db: Session):
    """
    Process a single campaign lead using the LangGraph workflow.
    
    Args:
        campaign_lead_id: ID of the CampaignLead to process
        db: Database session
    
    Returns:
        Dict with processing results
    """
    from app.models import CampaignLead, ProcessingLog
    
    logger.info(f"Starting LangGraph processing for CampaignLead {campaign_lead_id}")
    
    try:
        # Fetch the campaign lead with relationships
        campaign_lead = db.query(CampaignLead).filter(
            CampaignLead.id == campaign_lead_id
        ).first()
        
        if not campaign_lead:
            raise ValueError(f"CampaignLead {campaign_lead_id} not found")
        
        # Update status to processing
        campaign_lead.status = 'processing'
        db.commit()
        
        # Initialize state
        campaign = campaign_lead.campaign
        initial_state = initialize_lead_state(
            campaign_lead=campaign_lead,
            campaign=campaign,
            lead=campaign_lead.lead
        )
        
        # Create and run the graph
        # Priority: A2A > Dynamic > Static
        if initial_state.get('use_a2a'):
            logger.info(f"Using A2A graph for campaign {campaign.id}")
            graph = create_a2a_campaign_lead_graph()
        elif campaign.workflow_config:
            logger.info(f"Using dynamic graph for campaign {campaign.id}")
            graph = create_dynamic_campaign_lead_graph(campaign.workflow_config)
        else:
            logger.info(f"Using static graph for campaign {campaign.id}")
            graph = create_campaign_lead_graph()
        
        # Configure LangSmith tracing
        run_config = {}
        if settings.LANGCHAIN_TRACING_V2 and settings.LANGCHAIN_API_KEY:
            run_config["run_name"] = f"Campaign_{campaign.id}_Lead_{campaign_lead.lead.id}"
            run_config["tags"] = [
                f"campaign:{campaign.id}",
                f"lead:{campaign_lead.lead.id}",
                f"agent_type:{campaign.agent_type}"
            ]
            run_config["metadata"] = {
                "campaign_id": campaign.id,
                "campaign_name": campaign.name,
                "lead_id": campaign_lead.lead.id,
                "lead_name": campaign_lead.lead.name,
                "campaign_lead_id": campaign_lead.id
            }
            
        final_state = graph.invoke(initial_state, config=run_config)
        
        # Update campaign lead with results
        campaign_lead.status = final_state['status']
        campaign_lead.sms_sent = final_state['sms_sent']
        campaign_lead.sms_message = final_state['sms_message']
        campaign_lead.voice_call_made = final_state['voice_call_made']
        campaign_lead.error_message = final_state['error_message']
        campaign_lead.trace_id = final_state.get('trace_id', '')
        campaign_lead.processed_at = datetime.now()
        db.commit()
        
        # Save conversation messages to database
        from app.models import ConversationMessage
        for msg in final_state.get('conversation_history', []):
            conversation_msg = ConversationMessage(
                campaign_lead_id=campaign_lead.id,
                role=msg.get('role', 'assistant'),
                content=msg.get('content', ''),
                message_metadata=msg.get('metadata', {})
            )
            db.add(conversation_msg)
        db.commit()
        
        # Save processing logs
        for log_entry in final_state['processing_logs']:
            processing_log = ProcessingLog(
                campaign_lead_id=campaign_lead.id,
                level='INFO' if final_state['status'] == 'completed' else 'ERROR',
                node_name=log_entry['node'],
                message=log_entry['message'],
                log_metadata=log_entry
            )
            db.add(processing_log)
        db.commit()
        
        # Update campaign statistics
        campaign = campaign_lead.campaign
        campaign.update_stats()
        db.commit()
        
        logger.info(f"LangGraph processing complete for CampaignLead {campaign_lead_id}: {final_state['status']}")
        
        return {
            'success': final_state['status'] == 'completed',
            'status': final_state['status'],
            'sms_sent': final_state['sms_sent'],
            'voice_call_made': final_state['voice_call_made'],
            'error_message': final_state['error_message']
        }
        
    except Exception as e:
        logger.error(f"Error processing CampaignLead {campaign_lead_id}: {str(e)}")
        
        # Update campaign lead with error
        try:
            campaign_lead = db.query(CampaignLead).filter(
                CampaignLead.id == campaign_lead_id
            ).first()
            if campaign_lead:
                campaign_lead.status = 'failed'
                campaign_lead.error_message = str(e)
                campaign_lead.processed_at = datetime.now()
                db.commit()
                
                # Update campaign statistics
                campaign = campaign_lead.campaign
                campaign.update_stats()
                db.commit()
        except Exception as update_error:
            logger.error(f"Error updating CampaignLead after failure: {str(update_error)}")
        
        return {
            'success': False,
            'status': 'failed',
            'error_message': str(e)
        }

