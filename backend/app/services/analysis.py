"""Analysis service for extracting insights from transcripts."""
import os
import logging
from typing import Dict, Any, List
from openai import AsyncOpenAI
import json

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service for analyzing call transcripts to extract insights."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def analyze_transcript(
        self,
        transcript: str,
        segments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze transcript to extract insights.
        
        Args:
            transcript: Full transcript text
            segments: Transcript segments with timestamps
            
        Returns:
            Analysis results with tonality, hooks, objections, etc.
        """
        try:
            # Use LLM to analyze the transcript
            analysis_prompt = f"""Analyze this sales call transcript and extract key insights that would help replicate the sales rep's success.

Transcript:
{transcript}

Please provide a detailed analysis in JSON format with the following structure:

{{
  "tonality_description": "Description of the overall tone (e.g., 'confident and consultative', 'friendly and energetic')",
  "communication_style": {{
    "formality": "casual|neutral|formal",
    "energy": "low|medium|high",
    "pace": "slow|moderate|fast"
  }},
  "hooks": [
    {{
      "text": "The actual hook/opening line used",
      "effectiveness": "low|medium|high",
      "context": "When/why it was effective"
    }}
  ],
  "objections": [
    {{
      "objection": "The prospect's objection",
      "response": "How the rep handled it",
      "outcome": "resolved|unresolved",
      "technique": "Name of the technique used"
    }}
  ],
  "key_phrases": ["phrase1", "phrase2", "phrase3"],
  "conversation_flow": {{
    "opening": "Summary of opening approach",
    "discovery": "How they uncovered needs",
    "presentation": "How they presented solution",
    "closing": "Closing technique used"
  }},
  "success_patterns": {{
    "strengths": ["strength1", "strength2"],
    "unique_approaches": ["approach1", "approach2"],
    "rapport_building": "How they built rapport"
  }}
}}

Provide only the JSON response, no additional text."""

            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert sales coach and conversation analyst. Analyze sales calls to extract actionable insights."
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            analysis_result = json.loads(response.choices[0].message.content)
            
            # Add voice profile analysis
            from app.services.elevenlabs import ElevenLabsService
            elevenlabs = ElevenLabsService()
            voice_profile = await elevenlabs.analyze_voice_characteristics(segments)
            analysis_result["voice_profile"] = voice_profile
            
            # Recommend voice
            recommended_voice = elevenlabs.recommend_voice(
                analysis_result.get("tonality_description", ""),
                analysis_result.get("communication_style", {})
            )
            analysis_result["recommended_voice_id"] = recommended_voice
            
            return analysis_result
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing analysis JSON: {str(e)}")
            # Return a basic structure if parsing fails
            return self._get_fallback_analysis()
        except Exception as e:
            logger.error(f"Error analyzing transcript: {str(e)}")
            raise
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Return a basic analysis structure if LLM analysis fails."""
        return {
            "tonality_description": "Analysis in progress",
            "communication_style": {
                "formality": "neutral",
                "energy": "medium",
                "pace": "moderate"
            },
            "hooks": [],
            "objections": [],
            "key_phrases": [],
            "conversation_flow": {
                "opening": "Not analyzed",
                "discovery": "Not analyzed",
                "presentation": "Not analyzed",
                "closing": "Not analyzed"
            },
            "success_patterns": {
                "strengths": [],
                "unique_approaches": [],
                "rapport_building": "Not analyzed"
            },
            "voice_profile": {
                "speaking_rate_wpm": 0,
                "pace": "moderate",
                "recommended_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5,
                    "style": 0.5,
                    "use_speaker_boost": True
                }
            },
            "recommended_voice_id": "EXAVITQu4vr4xnSDxMaL"
        }
    
    async def extract_best_practices(
        self,
        multiple_analyses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract common best practices from multiple call analyses.
        
        Args:
            multiple_analyses: List of analysis results from different calls
            
        Returns:
            Consolidated best practices
        """
        if not multiple_analyses:
            return {}
        
        try:
            # Combine all analyses
            combined = {
                "all_hooks": [],
                "all_objections": [],
                "all_key_phrases": [],
                "common_patterns": []
            }
            
            for analysis in multiple_analyses:
                combined["all_hooks"].extend(analysis.get("hooks", []))
                combined["all_objections"].extend(analysis.get("objections", []))
                combined["all_key_phrases"].extend(analysis.get("key_phrases", []))
            
            # Use LLM to identify patterns
            synthesis_prompt = f"""Analyze these insights from multiple successful sales calls and identify common patterns and best practices.

Data:
{json.dumps(combined, indent=2)}

Provide a JSON response with:
{{
  "most_effective_hooks": ["hook1", "hook2"],
  "best_objection_techniques": ["technique1", "technique2"],
  "common_success_patterns": ["pattern1", "pattern2"],
  "recommended_approach": "Overall recommended approach based on all calls"
}}"""

            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at identifying patterns in sales conversations."
                    },
                    {
                        "role": "user",
                        "content": synthesis_prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error extracting best practices: {str(e)}")
            return {}
