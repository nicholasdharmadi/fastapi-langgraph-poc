"""LangGraph node implementations for campaign processing."""
import logging
from typing import Dict, Any
from datetime import datetime
from app.orchestrator.state import CampaignLeadState
from app.config import settings

logger = logging.getLogger(__name__)


def validate_lead_node(state: CampaignLeadState) -> CampaignLeadState:
    """Validate lead data before processing."""
    logger.info(f"[ValidateNode] Processing lead {state['lead_id']}")
    
    lead_data = state['lead_data']
    errors = []
    
    # Check required fields
    if not lead_data.get('phone'):
        errors.append("Missing phone number")
    
    if not lead_data.get('name'):
        errors.append("Missing name")
    
    # Working hours check (configurable)
    if settings.ENFORCE_WORKING_HOURS:
        current_hour = datetime.now().hour
        current_weekday = datetime.now().weekday()  # 0=Monday, 6=Sunday
        
        # Check weekend
        if not settings.ALLOW_WEEKEND_SENDING and current_weekday >= 5:  # Saturday or Sunday
            errors.append(f"Weekend sending disabled (current day: {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][current_weekday]})")
        
        # Check hours
        if not (settings.WORKING_HOURS_START <= current_hour < settings.WORKING_HOURS_END):
            errors.append(f"Outside working hours (current: {current_hour}:00, allowed: {settings.WORKING_HOURS_START}:00-{settings.WORKING_HOURS_END}:00)")
    
    # Update state
    state['validation_passed'] = len(errors) == 0
    state['validation_errors'] = errors
    
    state['processing_logs'].append({
        'node': 'validate_lead',
        'timestamp': datetime.now().isoformat(),
        'message': f"Validation {'passed' if state['validation_passed'] else 'failed'}",
        'errors': errors
    })
    
    logger.info(f"[ValidateNode] Validation result: {state['validation_passed']}")
    return state


def sms_agent_node(state: CampaignLeadState) -> CampaignLeadState:
    """Process SMS using OpenAI agent."""
    logger.info(f"[SMSNode] Processing SMS for lead {state['lead_id']}")
    
    try:
        from app.services.openai_service import OpenAIService
        
        service = OpenAIService()
        lead_data = state['lead_data']
        
        # Generate personalized SMS message
        result = service.generate_sms_message(
            system_prompt=state['sms_system_prompt'],
            lead_data=lead_data,
            temperature=state['sms_temperature']
        )
        
        if not result.get('success', False):
            state['sms_message'] = ''
            state['sms_sent'] = False
            state['sms_error'] = result.get('error', 'SMS generation failed')
            state['sms_cost'] = 0.0
            state['processing_logs'].append({
                'node': 'sms_agent',
                'timestamp': datetime.now().isoformat(),
                'message': 'SMS generation failed',
                'error': state['sms_error']
            })
            logger.error(f"[SMSNode] SMS generation failed: {state['sms_error']}")
            return state
        
        state['sms_message'] = result.get('message', '')
        state['sms_cost'] = result.get('cost', 0.0)
        
        # Log conversation to history
        state['conversation_history'].append({
            'role': 'system',
            'content': state['sms_system_prompt'],
            'metadata': {'node': 'sms_agent', 'step': 'system_prompt'}
        })
        state['conversation_history'].append({
            'role': 'assistant',
            'content': state['sms_message'],
            'metadata': {'node': 'sms_agent', 'step': 'generated_message', 'cost': state['sms_cost']}
        })
        
        # For POC, we're using mock SMS sending
        # In production, integrate with Twilio here
        from app.services.sms_service import SMSService
        sms_service = SMSService()
        send_result = sms_service.send_sms(
            to=lead_data['phone'],
            message=state['sms_message']
        )
        
        state['sms_sent'] = send_result['success']
        state['sms_error'] = send_result.get('error', '')
        
        state['processing_logs'].append({
            'node': 'sms_agent',
            'timestamp': datetime.now().isoformat(),
            'message': f"SMS {'sent' if state['sms_sent'] else 'failed'}",
            'sms_message': state['sms_message'][:100],
            'error': state['sms_error']
        })
        
        logger.info(f"[SMSNode] SMS result: {state['sms_sent']}")
        
    except Exception as e:
        logger.error(f"[SMSNode] Error: {str(e)}")
        state['sms_sent'] = False
        state['sms_error'] = str(e)
        state['sms_cost'] = 0.0
        state['processing_logs'].append({
            'node': 'sms_agent',
            'timestamp': datetime.now().isoformat(),
            'message': 'SMS processing failed',
            'error': str(e)
        })
    
    return state


def voice_agent_node(state: CampaignLeadState) -> CampaignLeadState:
    """Process voice call (mocked for POC)."""
    logger.info(f"[VoiceNode] Processing voice call for lead {state['lead_id']}")
    
    # Voice agent is mocked for POC
    state['voice_call_made'] = True
    state['voice_call_id'] = f"mock_call_{state['lead_id']}"
    state['voice_error'] = ''
    state['voice_cost'] = 0.0
    
    state['processing_logs'].append({
        'node': 'voice_agent',
        'timestamp': datetime.now().isoformat(),
        'message': 'Voice call initiated (mocked)',
        'call_id': state['voice_call_id']
    })
    
    logger.info(f"[VoiceNode] Voice call result: {state['voice_call_made']}")
    logger.info(f"[VoiceNode] Voice call result: {state['voice_call_made']}")
    return state


def enrichment_node(state: CampaignLeadState) -> CampaignLeadState:
    """Enrich lead data (mocked for POC)."""
    logger.info(f"[EnrichmentNode] Enriching data for lead {state['lead_id']}")
    
    try:
        # Mock enrichment logic
        # In production, call Clearbit, Apollo, etc.
        lead_data = state['lead_data']
        
        # Simulate finding data based on email domain or company
        enriched_info = {}
        if lead_data.get('company'):
            enriched_info['industry'] = 'Technology'
            enriched_info['size'] = '100-500'
            enriched_info['location'] = 'San Francisco, CA'
        
        state['enrichment_data'] = enriched_info
        state['enrichment_error'] = ''
        
        # Merge enriched data into lead_data for downstream nodes
        state['lead_data'] = {**lead_data, **enriched_info}
        
        state['processing_logs'].append({
            'node': 'enrichment_node',
            'timestamp': datetime.now().isoformat(),
            'message': 'Data enrichment successful',
            'data': enriched_info
        })
        
        logger.info(f"[EnrichmentNode] Enrichment successful: {enriched_info}")
        
    except Exception as e:
        logger.error(f"[EnrichmentNode] Error: {str(e)}")
        state['enrichment_error'] = str(e)
        state['processing_logs'].append({
            'node': 'enrichment_node',
            'timestamp': datetime.now().isoformat(),
            'message': 'Data enrichment failed',
            'error': str(e)
        })
    
    return state


def finalize_node(state: CampaignLeadState) -> CampaignLeadState:
    """Finalize processing and determine overall status."""
    logger.info(f"[FinalizeNode] Finalizing lead {state['lead_id']}")
    
    if not state['validation_passed']:
        state['status'] = 'failed'
        state['error_message'] = '; '.join(state['validation_errors'])
    else:
        agent_type = state['agent_type']
        
        if agent_type == 'sms':
            state['status'] = 'completed' if state['sms_sent'] else 'failed'
            if not state['sms_sent']:
                state['error_message'] = state['sms_error']
        
        elif agent_type == 'voice':
            state['status'] = 'completed' if state['voice_call_made'] else 'failed'
            if not state['voice_call_made']:
                state['error_message'] = state['voice_error']
        
        elif agent_type == 'both':
            if state['sms_sent'] and state['voice_call_made']:
                state['status'] = 'completed'
            else:
                state['status'] = 'failed'
                errors = []
                if not state['sms_sent']:
                    errors.append(f"SMS: {state['sms_error']}")
                if not state['voice_call_made']:
                    errors.append(f"Voice: {state['voice_error']}")
                state['error_message'] = '; '.join(errors)
    
    state['processing_logs'].append({
        'node': 'finalize',
        'timestamp': datetime.now().isoformat(),
        'message': f"Processing {state['status']}",
        'final_status': state['status']
    })
    
    logger.info(f"[FinalizeNode] Final status: {state['status']}")
    return state


def route_after_validation(state: CampaignLeadState) -> str:
    """Conditional routing after validation."""
    if not state['validation_passed']:
        logger.info("[Router] Validation failed, skipping to finalize")
        return "finalize"
    
    agent_type = state['agent_type']
    logger.info(f"[Router] Routing to {agent_type} agent(s)")
    
    if agent_type == 'sms':
        return "sms_only"
    elif agent_type == 'voice':
        return "voice_only"
    else:  # 'both'
        return "sms_first"


def route_after_sms(state: CampaignLeadState) -> str:
    """Conditional routing after SMS."""
    if state['agent_type'] == 'both':
        logger.info("[Router] SMS complete, proceeding to voice")
        return "voice"
    else:
        logger.info("[Router] SMS complete, finalizing")
        return "finalize"

