"""Prompt generation service using LLM to create system prompts from analysis."""
import os
import logging
from typing import Dict, Any, Optional
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class PromptGeneratorService:
    """Service for generating system prompts from call analysis."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def generate_system_prompt(
        self,
        transcript: str,
        analysis: Dict[str, Any]
    ) -> str:
        """
        Generate a system prompt based on transcript and analysis.
        
        Args:
            transcript: Full transcript text
            analysis: Analysis results containing tonality, hooks, objections, etc.
            
        Returns:
            Generated system prompt
        """
        # Build the analysis summary
        analysis_summary = self._build_analysis_summary(analysis)
        
        # Create the generation prompt
        generation_prompt = f"""You are an expert at creating system prompts for AI sales agents. 

I have analyzed a successful sales call recording and extracted key insights. Your task is to create a comprehensive system prompt that will enable an AI agent (using LLM + Text-to-Speech) to replicate the successful patterns from this call.

## Call Analysis

{analysis_summary}

## Sample Transcript Excerpts
{self._extract_key_excerpts(transcript, analysis)}

## Your Task

Create a detailed system prompt that includes:

1. **Role & Persona**: Define the agent's identity and personality based on the tonality analysis
2. **Communication Style**: Specify how the agent should communicate (pace, formality, energy level)
3. **Opening Strategy**: How to start conversations using identified hooks
4. **Discovery Framework**: Question patterns and conversation flow
5. **Objection Handling**: Specific responses to common objections with examples
6. **Closing Techniques**: How to move towards conversion
7. **Voice Guidelines**: Instructions for TTS (pitch, speed, emphasis, pauses)
8. **Example Exchanges**: Include actual successful snippets from the transcript

The prompt should be actionable, specific, and capture the essence of what made this sales rep successful.

Generate the system prompt now:"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing sales conversations and creating effective system prompts for AI agents."
                    },
                    {
                        "role": "user",
                        "content": generation_prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating prompt: {str(e)}")
            raise
    
    def _build_analysis_summary(self, analysis: Dict[str, Any]) -> str:
        """Build a formatted summary of the analysis."""
        summary_parts = []
        
        # Tonality
        if analysis.get("tonality_description"):
            summary_parts.append(f"**Tonality**: {analysis['tonality_description']}")
        
        # Communication Style
        if analysis.get("communication_style"):
            style = analysis["communication_style"]
            summary_parts.append(
                f"**Communication Style**: "
                f"Formality: {style.get('formality', 'N/A')}, "
                f"Energy: {style.get('energy', 'N/A')}, "
                f"Pace: {style.get('pace', 'N/A')}"
            )
        
        # Hooks
        if analysis.get("hooks"):
            hooks_text = "\n".join([f"- {h.get('text', '')}" for h in analysis["hooks"][:5]])
            summary_parts.append(f"**Effective Hooks**:\n{hooks_text}")
        
        # Objections
        if analysis.get("objections"):
            obj_text = "\n".join([
                f"- Objection: {o.get('objection', '')}\n  Response: {o.get('response', '')}"
                for o in analysis["objections"][:3]
            ])
            summary_parts.append(f"**Objection Handling**:\n{obj_text}")
        
        # Key Phrases
        if analysis.get("key_phrases"):
            phrases = ", ".join(analysis["key_phrases"][:10])
            summary_parts.append(f"**Key Phrases**: {phrases}")
        
        # Voice Profile
        if analysis.get("voice_profile"):
            vp = analysis["voice_profile"]
            summary_parts.append(
                f"**Voice Characteristics**: "
                f"Speaking rate: {vp.get('speaking_rate_wpm', 'N/A')} WPM, "
                f"Pace: {vp.get('pace', 'N/A')}"
            )
        
        return "\n\n".join(summary_parts)
    
    def _extract_key_excerpts(
        self, 
        transcript: str, 
        analysis: Dict[str, Any]
    ) -> str:
        """Extract key excerpts from transcript based on analysis."""
        excerpts = []
        
        # Add hook examples
        if analysis.get("hooks"):
            for hook in analysis["hooks"][:3]:
                if "text" in hook:
                    excerpts.append(f"[Opening Hook]: {hook['text']}")
        
        # Add objection handling examples
        if analysis.get("objections"):
            for obj in analysis["objections"][:2]:
                if "objection" in obj and "response" in obj:
                    excerpts.append(
                        f"[Objection Handling]\n"
                        f"Prospect: {obj['objection']}\n"
                        f"Rep: {obj['response']}"
                    )
        
        # If no specific excerpts, take first 500 chars
        if not excerpts:
            excerpts.append(transcript[:500] + "...")
        
        return "\n\n".join(excerpts)
    
    async def refine_prompt(
        self,
        original_prompt: str,
        feedback: str
    ) -> str:
        """
        Refine an existing prompt based on feedback.
        
        Args:
            original_prompt: The current system prompt
            feedback: User feedback or performance data
            
        Returns:
            Refined system prompt
        """
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at refining system prompts for AI agents based on feedback."
                    },
                    {
                        "role": "user",
                        "content": f"""Here is a system prompt for an AI sales agent:

{original_prompt}

Feedback/Performance Data:
{feedback}

Please refine the system prompt to address the feedback while maintaining the core successful patterns. Return only the refined prompt."""
                    }
                ],
                temperature=0.7,
                max_tokens=2500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error refining prompt: {str(e)}")
            raise
