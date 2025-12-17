"""OpenAI service for SMS agent using LangChain."""
import logging
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.config import settings

logger = logging.getLogger(__name__)

# Make LangSmith tracing optional
try:
    from langsmith import traceable
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    def traceable(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


class OpenAIService:
    """Service for interacting with OpenAI via LangChain."""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        if not self.api_key:
            logger.warning("OpenAI API key not configured")
    
    @traceable(name="generate_sms_message")
    def generate_sms_message(
        self, 
        system_prompt: str, 
        lead_data: Dict[str, Any],
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate a personalized SMS message using OpenAI.
        
        Args:
            system_prompt: The agent's system prompt
            lead_data: Lead information (name, phone, etc.)
            temperature: LLM temperature (0.0-1.0)
        
        Returns:
            Dict with 'success', 'message', 'cost', and optional 'error'
        """
        try:
            # Initialize LangChain ChatOpenAI
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=temperature,
                api_key=self.api_key
            )
            
            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", """Generate a professional SMS message for this lead:

Name: {name}
Phone: {phone}
Email: {email}
Company: {company}

Keep the message under 160 characters, friendly, and professional.
Only return the SMS text, nothing else.""")
            ])
            
            # Format the prompt with lead data
            messages = prompt.format_messages(**lead_data)
            
            # Generate the message
            response = llm.invoke(messages)
            sms_message = response.content.strip()
            
            # Extract token usage
            token_usage = response.response_metadata.get('token_usage', {})
            if not token_usage and hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                token_usage = {
                    'prompt_tokens': usage.get('input_tokens', 0),
                    'completion_tokens': usage.get('output_tokens', 0),
                    'total_tokens': usage.get('total_tokens', 0)
                }
            
            # Calculate cost (GPT-4o-mini: $0.15/$0.60 per 1M tokens)
            cost = 0.0
            if token_usage:
                input_tokens = token_usage.get('prompt_tokens', 0)
                output_tokens = token_usage.get('completion_tokens', 0)
                input_cost = (input_tokens / 1_000_000) * 0.15
                output_cost = (output_tokens / 1_000_000) * 0.60
                cost = input_cost + output_cost
            
            logger.info(f"Generated SMS: {sms_message[:50]}...")
            logger.info(f"Token usage: {token_usage}, Cost: ${cost:.6f}")
            
            return {
                'success': True,
                'message': sms_message,
                'tokens_used': token_usage,
                'cost': cost
            }
            
        except Exception as e:
            logger.error(f"Error generating SMS message: {str(e)}")
            return {
                'success': False,
                'message': '',
                'error': str(e),
                'cost': 0.0
            }
    
    @traceable(name="generate_message_with_agent")
    def generate_message_with_agent(
        self,
        agent_id: str,
        system_prompt: str,
        model: str,
        context: Dict[str, Any],
        temperature: float = 0.7,
        conversation_history: list = None
    ) -> Dict[str, Any]:
        """
        Generate a message using a specific agent configuration.
        Used in A2A workflows where different agents have different roles.
        
        Args:
            agent_id: ID of the agent
            system_prompt: The agent's system prompt
            model: Model to use (e.g., "gpt-4o", "gpt-4o-mini")
            context: Context data (lead info, enrichment data, etc.)
            temperature: LLM temperature (0.0-1.0)
            conversation_history: Previous conversation messages
        
        Returns:
            Dict with 'success', 'message', 'cost', and optional 'error'
        """
        try:
            # Initialize LangChain ChatOpenAI with specified model
            llm = ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=self.api_key
            )
            
            # Build messages list
            messages = [("system", system_prompt)]
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history:
                    role = msg.get('role', 'assistant')
                    content = msg.get('content', '')
                    if role == 'system':
                        continue  # Skip system messages from history
                    messages.append((role, content))
            
            # Add current context as human message
            context_str = f"""Generate a professional SMS message for this lead:

Name: {context.get('name', 'Unknown')}
Phone: {context.get('phone', 'Unknown')}
Email: {context.get('email', 'Unknown')}
Company: {context.get('company', 'Unknown')}"""
            
            # Add enrichment data if available
            if context.get('industry') or context.get('size') or context.get('location'):
                context_str += "\n\nEnriched Data:"
                if context.get('industry'):
                    context_str += f"\nIndustry: {context['industry']}"
                if context.get('size'):
                    context_str += f"\nCompany Size: {context['size']}"
                if context.get('location'):
                    context_str += f"\nLocation: {context['location']}"
            
            context_str += "\n\nKeep the message under 160 characters, friendly, and professional.\nOnly return the SMS text, nothing else."
            
            messages.append(("human", context_str))
            
            # Create prompt and generate
            prompt = ChatPromptTemplate.from_messages(messages)
            formatted_messages = prompt.format_messages()
            
            response = llm.invoke(formatted_messages)
            message = response.content.strip()
            
            # Extract token usage
            token_usage = response.response_metadata.get('token_usage', {})
            if not token_usage and hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                token_usage = {
                    'prompt_tokens': usage.get('input_tokens', 0),
                    'completion_tokens': usage.get('output_tokens', 0),
                    'total_tokens': usage.get('total_tokens', 0)
                }
            
            # Calculate cost based on model
            cost = 0.0
            if token_usage:
                input_tokens = token_usage.get('prompt_tokens', 0)
                output_tokens = token_usage.get('completion_tokens', 0)
                
                # Pricing varies by model
                if 'gpt-4o-mini' in model:
                    input_cost = (input_tokens / 1_000_000) * 0.15
                    output_cost = (output_tokens / 1_000_000) * 0.60
                elif 'gpt-4o' in model:
                    input_cost = (input_tokens / 1_000_000) * 2.50
                    output_cost = (output_tokens / 1_000_000) * 10.00
                else:
                    # Default to gpt-4o-mini pricing
                    input_cost = (input_tokens / 1_000_000) * 0.15
                    output_cost = (output_tokens / 1_000_000) * 0.60
                
                cost = input_cost + output_cost
            
            logger.info(f"Agent {agent_id} generated message: {message[:50]}...")
            logger.info(f"Model: {model}, Token usage: {token_usage}, Cost: ${cost:.6f}")
            
            return {
                'success': True,
                'message': message,
                'tokens_used': token_usage,
                'cost': cost,
                'model': model,
                'agent_id': agent_id
            }
            
        except Exception as e:
            logger.error(f"Error generating message with agent {agent_id}: {str(e)}")
            return {
                'success': False,
                'message': '',
                'error': str(e),
                'cost': 0.0
            }

