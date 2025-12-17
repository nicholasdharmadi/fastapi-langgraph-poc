"""SMS service for sending messages (mock implementation for POC)."""
import logging
from typing import Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)


class SMSService:
    """Service for sending SMS messages."""
    
    def __init__(self):
        self.provider = settings.SMS_PROVIDER
    
    def send_sms(self, to: str, message: str) -> Dict[str, Any]:
        """
        Send an SMS message.
        
        Args:
            to: Phone number to send to
            message: SMS message content
        
        Returns:
            Dict with 'success' and optional 'error'
        """
        if self.provider == "mock":
            return self._send_mock_sms(to, message)
        elif self.provider == "twilio":
            return self._send_twilio_sms(to, message)
        else:
            return {
                'success': False,
                'error': f"Unknown SMS provider: {self.provider}"
            }
    
    def _send_mock_sms(self, to: str, message: str) -> Dict[str, Any]:
        """Mock SMS sending for POC."""
        logger.info(f"[MOCK SMS] To: {to}, Message: {message[:50]}...")
        return {
            'success': True,
            'message_id': f"mock_{to}_{len(message)}"
        }
    
    def _send_twilio_sms(self, to: str, message: str) -> Dict[str, Any]:
        """Send SMS via Twilio (requires configuration)."""
        try:
            from twilio.rest import Client
            
            if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
                logger.warning("Twilio not configured, falling back to mock")
                return self._send_mock_sms(to, message)
            
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            message_obj = client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to
            )
            
            logger.info(f"[TWILIO SMS] Sent message {message_obj.sid} to {to}")
            
            return {
                'success': True,
                'message_id': message_obj.sid,
                'status': message_obj.status
            }
            
        except Exception as e:
            logger.error(f"Error sending Twilio SMS: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

