"""ElevenLabs service for transcription and TTS integration."""
import os
import httpx
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class ElevenLabsService:
    """Service for interacting with ElevenLabs API."""
    
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            logger.warning("ELEVENLABS_API_KEY not set")
        
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key,
        }
    
    async def transcribe_audio(self, file_path: str) -> Dict[str, Any]:
        """
        Transcribe audio file using ElevenLabs.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dict containing transcript and metadata
        """
        try:
            # Note: ElevenLabs doesn't have a direct transcription API
            # We'll use their speech-to-text if available, or fall back to OpenAI Whisper
            # For now, implementing with OpenAI Whisper as fallback
            
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            with open(file_path, "rb") as audio_file:
                transcript = await client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["segment"]
                )
            
            # Convert to our format
            segments = []
            if hasattr(transcript, 'segments') and transcript.segments:
                for seg in transcript.segments:
                    segments.append({
                        "text": seg.get("text", ""),
                        "start": seg.get("start", 0.0),
                        "end": seg.get("end", 0.0),
                        "speaker": "unknown"  # Whisper doesn't do speaker diarization
                    })
            
            return {
                "full_text": transcript.text,
                "segments": segments,
                "duration": getattr(transcript, 'duration', None),
                "language": getattr(transcript, 'language', None),
            }
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            raise
    
    async def get_voices(self) -> List[Dict[str, Any]]:
        """
        Get available ElevenLabs voices.
        
        Returns:
            List of voice configurations
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/voices",
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("voices", [])
        except Exception as e:
            logger.error(f"Error fetching voices: {str(e)}")
            return []
    
    async def analyze_voice_characteristics(
        self, 
        transcript_segments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze voice characteristics from transcript for TTS matching.
        
        Args:
            transcript_segments: List of transcript segments with timing
            
        Returns:
            Voice profile with recommended settings
        """
        # Analyze speaking patterns
        total_duration = 0
        total_words = 0
        
        for segment in transcript_segments:
            duration = segment.get("end", 0) - segment.get("start", 0)
            words = len(segment.get("text", "").split())
            total_duration += duration
            total_words += words
        
        # Calculate speaking rate (words per minute)
        wpm = (total_words / total_duration * 60) if total_duration > 0 else 0
        
        # Determine pace
        if wpm < 120:
            pace = "slow"
            stability = 0.7
            similarity_boost = 0.3
        elif wpm < 160:
            pace = "moderate"
            stability = 0.5
            similarity_boost = 0.5
        else:
            pace = "fast"
            stability = 0.3
            similarity_boost = 0.7
        
        return {
            "speaking_rate_wpm": round(wpm, 1),
            "pace": pace,
            "recommended_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": 0.5,  # Default
                "use_speaker_boost": True
            }
        }
    
    def recommend_voice(
        self, 
        tonality: str, 
        communication_style: Dict[str, Any]
    ) -> str:
        """
        Recommend an ElevenLabs voice based on analysis.
        
        Args:
            tonality: Description of tonality
            communication_style: Style characteristics
            
        Returns:
            Recommended voice_id
        """
        # Map characteristics to ElevenLabs voices
        # These are example voice IDs - adjust based on available voices
        
        energy = communication_style.get("energy", "medium")
        formality = communication_style.get("formality", "neutral")
        
        # Professional, energetic
        if formality == "formal" and energy == "high":
            return "21m00Tcm4TlvDq8ikWAM"  # Rachel - professional female
        
        # Casual, friendly
        elif formality == "casual" and energy == "high":
            return "pNInz6obpgDQGcFmaJgB"  # Adam - friendly male
        
        # Calm, authoritative
        elif energy == "low":
            return "VR6AewLTigWG4xSOukaG"  # Arnold - deep, calm
        
        # Default: balanced
        else:
            return "EXAVITQu4vr4xnSDxMaL"  # Bella - neutral, clear
    
    async def generate_speech_sample(
        self,
        text: str,
        voice_id: str,
        voice_settings: Dict[str, Any]
    ) -> bytes:
        """
        Generate a speech sample for testing.
        
        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID
            voice_settings: Voice configuration
            
        Returns:
            Audio bytes
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/text-to-speech/{voice_id}",
                    headers={
                        **self.headers,
                        "Content-Type": "application/json"
                    },
                    json={
                        "text": text,
                        "model_id": "eleven_monolingual_v1",
                        "voice_settings": voice_settings
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                return response.content
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            raise
