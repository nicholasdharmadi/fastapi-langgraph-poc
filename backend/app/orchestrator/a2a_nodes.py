"""A2A (Agent-to-Agent) orchestration nodes for dual-agent workflows."""
import logging
from typing import Dict, Any
from datetime import datetime
from app.orchestrator.state import CampaignLeadState
from app.config import settings

logger = logging.getLogger(__name__)


def a2a_creative_agent_node(state: CampaignLeadState) -> CampaignLeadState:
    """
    Creative agent node - handles conversation, message generation, and context.
    This agent focuses on natural language, personalization, and engagement.
    """
    logger.info(f"[A2A-CreativeAgent] Processing lead {state['lead_id']}")
    
    if not state['use_a2a']:
        logger.warning("[A2A-CreativeAgent] A2A not enabled, skipping")
        return state
    
    try:
        from app.services.openai_service import OpenAIService
        
        service = OpenAIService()
        lead_data = state['lead_data']
        
        # Build context for creative agent
        # Include any enrichment data from deterministic agent
        context = {
            **lead_data,
            **state.get('enrichment_data', {})
        }
        
        # Generate personalized message using creative agent
        result = service.generate_message_with_agent(
            agent_id=state['creative_agent_id'],
            system_prompt=state['creative_agent_prompt'],
            model=state['creative_agent_model'],
            context=context,
            temperature=state.get('sms_temperature', 0.7),
            conversation_history=state.get('conversation_history', [])
        )
        
        if not result.get('success', False):
            state['sms_error'] = result.get('error', 'Creative agent failed')
            state['processing_logs'].append({
                'node': 'a2a_creative_agent',
                'timestamp': datetime.now().isoformat(),
                'message': 'Creative agent failed',
                'error': state['sms_error']
            })
            logger.error(f"[A2A-CreativeAgent] Failed: {state['sms_error']}")
            return state
        
        # Store creative agent output
        state['sms_message'] = result.get('message', '')
        state['sms_cost'] = result.get('cost', 0.0)
        
        # Log to conversation history
        state['conversation_history'].append({
            'role': 'assistant',
            'agent': 'creative',
            'agent_id': state['creative_agent_id'],
            'content': state['sms_message'],
            'metadata': {
                'node': 'a2a_creative_agent',
                'cost': state['sms_cost'],
                'model': state['creative_agent_model']
            }
        })
        
        state['processing_logs'].append({
            'node': 'a2a_creative_agent',
            'timestamp': datetime.now().isoformat(),
            'message': 'Creative agent generated message',
            'message_preview': state['sms_message'][:100]
        })
        
        logger.info(f"[A2A-CreativeAgent] Generated message: {state['sms_message'][:50]}...")
        
    except Exception as e:
        logger.error(f"[A2A-CreativeAgent] Error: {str(e)}")
        state['sms_error'] = str(e)
        state['processing_logs'].append({
            'node': 'a2a_creative_agent',
            'timestamp': datetime.now().isoformat(),
            'message': 'Creative agent processing failed',
            'error': str(e)
        })
    
    return state


def a2a_deterministic_agent_node(state: CampaignLeadState) -> CampaignLeadState:
    """
    Deterministic agent node - handles tool calling, API integrations, and structured operations.
    This agent focuses on executing actions, calling tools, and gathering data.
    """
    logger.info(f"[A2A-DeterministicAgent] Processing lead {state['lead_id']}")
    
    if not state['use_a2a']:
        logger.warning("[A2A-DeterministicAgent] A2A not enabled, skipping")
        return state
    
    try:
        from app.services.openai_service import OpenAIService
        
        service = OpenAIService()
        lead_data = state['lead_data']
        
        # Deterministic agent can execute tools
        # Examples: send SMS, make API calls, check calendars, etc.
        available_tools = state.get('deterministic_agent_tools', [])
        
        # Execute tool calls based on creative agent's output
        # For now, we'll handle SMS sending here
        if state.get('sms_message'):
            from app.services.sms_service import SMSService
            sms_service = SMSService()
            
            send_result = sms_service.send_sms(
                to=lead_data['phone'],
                message=state['sms_message']
            )
            
            state['sms_sent'] = send_result['success']
            state['sms_error'] = send_result.get('error', '') if not send_result['success'] else ''
            
            # Log tool execution
            state['conversation_history'].append({
                'role': 'tool',
                'agent': 'deterministic',
                'agent_id': state['deterministic_agent_id'],
                'content': f"SMS sent to {lead_data['phone']}",
                'metadata': {
                    'node': 'a2a_deterministic_agent',
                    'tool': 'send_sms',
                    'success': state['sms_sent'],
                    'error': state['sms_error']
                }
            })
            
            state['processing_logs'].append({
                'node': 'a2a_deterministic_agent',
                'timestamp': datetime.now().isoformat(),
                'message': f"SMS {'sent' if state['sms_sent'] else 'failed'}",
                'tool': 'send_sms',
                'success': state['sms_sent']
            })
            
            logger.info(f"[A2A-DeterministicAgent] SMS result: {state['sms_sent']}")
        
        # Execute other tools if configured
        for tool_config in available_tools:
            tool_name = tool_config.get('name')
            logger.info(f"[A2A-DeterministicAgent] Tool available: {tool_name}")
            # Tool execution logic would go here
            # Examples: calendly_check_availability, crm_update_lead, etc.
        
    except Exception as e:
        logger.error(f"[A2A-DeterministicAgent] Error: {str(e)}")
        state['sms_error'] = str(e)
        state['processing_logs'].append({
            'node': 'a2a_deterministic_agent',
            'timestamp': datetime.now().isoformat(),
            'message': 'Deterministic agent processing failed',
            'error': str(e)
        })
    
    return state


def a2a_handoff_node(state: CampaignLeadState) -> CampaignLeadState:
    """
    Handoff node - coordinates between creative and deterministic agents.
    Determines which agent should act next based on the current state.
    """
    logger.info(f"[A2A-Handoff] Coordinating agents for lead {state['lead_id']}")
    
    state['processing_logs'].append({
        'node': 'a2a_handoff',
        'timestamp': datetime.now().isoformat(),
        'message': 'Agent handoff coordination',
        'creative_complete': bool(state.get('sms_message')),
        'deterministic_complete': state.get('sms_sent', False)
    })
    
    return state


def route_a2a_workflow(state: CampaignLeadState) -> str:
    """
    Router for A2A workflow.
    Determines the next step in the agent-to-agent collaboration.
    """
    if not state['validation_passed']:
        logger.info("[A2A-Router] Validation failed, skipping to finalize")
        return "finalize"
    
    # If creative agent hasn't generated message yet
    if not state.get('sms_message'):
        logger.info("[A2A-Router] Routing to creative agent")
        return "creative"
    
    # If message generated but not sent
    if state.get('sms_message') and not state.get('sms_sent'):
        logger.info("[A2A-Router] Routing to deterministic agent")
        return "deterministic"
    
    # Both agents complete
    logger.info("[A2A-Router] Both agents complete, finalizing")
    return "finalize"
