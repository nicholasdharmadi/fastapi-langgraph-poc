import json
from sqlalchemy.orm import Session
from app.models.recording import PromptChatSession, GeneratedPrompt, PromptSourceType
from app.config import settings
import openai
from typing import List, Dict, Any

SYSTEM_PROMPT = """You are an expert AI Prompt Engineer. Your goal is to interview the user to build a robust system prompt for an AI agent.

The final prompt you are aiming to build should have these sections:
- Personality
- Environment
- Tone
- Goal
- Guardrails
- Tools
- Character normalization
- Error handling

**IMPORTANT RULES:**
1. **Ask ONLY ONE question at a time.** Never ask about multiple sections in a single message.
2. **Be concise.** Keep your responses short (1-2 sentences). Avoid long explanations unless explicitly asked.
3. **Be interactive.** Wait for the user's answer before moving to the next section.
4. **Guide the user.** If they give a vague answer, ask a clarifying question before moving on.
5. **OUTPUT FORMAT:** You must ALWAYS respond in valid JSON format with two fields:
   - "message": Your conversational response to the user.
   - "draft_prompt": The current state of the system prompt. Follow the EXACT formatting patterns shown in the examples below.

**CRITICAL: Section Formatting Templates**

Use these EXACT patterns for each section. Replace [CONTEXT] with user's specific details:

**# Personality**
```
You are a [ROLE] for [COMPANY/CONTEXT].
You are [TRAIT1], [TRAIT2], and focused on [PRIMARY FOCUS].
You speak [COMMUNICATION STYLE] while [ADDITIONAL BEHAVIOR].
```

**# Environment**
```
You are assisting [TARGET AUDIENCE] via [CHANNEL].
[AUDIENCE] may be [SITUATION/CONTEXT].
You have access to [TOOLS/RESOURCES].
```

**# Tone**
```
Keep responses [LENGTH GUIDELINE].
Use a [TONE DESCRIPTION] with [SPECIFIC PHRASES].
Adapt [WHAT] based on [CRITERIA].
Check for understanding after [WHEN]: "[EXAMPLE PHRASE]"
```

**# Goal**
```
[PRIMARY OBJECTIVE] through [METHOD]:

1. [STEP 1]
2. [STEP 2]
3. [STEP 3]
4. [STEP 4]

This step is important: [CRITICAL INSTRUCTION].
```

**# Guardrails**
```
Never [FORBIDDEN ACTION 1]. This step is important.
Never [FORBIDDEN ACTION 2]—always [REQUIRED ALTERNATIVE].
If [CONDITION], [ACTION].
Acknowledge when you don't know the answer instead of [WHAT TO AVOID].
```

**# Tools**
```
## `toolName`

**When to use:** [TRIGGER CONDITION]
**Parameters:**

- `param1` (required): [DESCRIPTION]
- `param2` (optional): [DESCRIPTION]

**Usage:**

1. [STEP 1]
2. [STEP 2]
3. [STEP 3]

**Error handling:**
If [ERROR CONDITION], [ACTION]: "[EXAMPLE RESPONSE]"
```

**# Character normalization**
```
When collecting [DATA TYPE]:

- Spoken: "[SPOKEN FORMAT]"
- Written: "[WRITTEN FORMAT]"
- Convert [RULES]
```

**# Error handling**
```
If any tool call fails:

1. Acknowledge: "[EXAMPLE RESPONSE]"
2. Do not [WHAT TO AVOID]
3. Offer to [ACTION], then [ESCALATION] if failure persists
```

**COMPLETE EXAMPLE (showing all sections together):**
```
# Personality
You are a technical support specialist for CloudTech, a B2B SaaS platform.
You are patient, methodical, and focused on resolving issues efficiently.
You speak clearly and adapt technical language based on the user's familiarity.

# Environment
You are assisting customers via phone support.
Customers may be experiencing service disruptions and could be frustrated.
You have access to diagnostic tools and the customer account database.

# Tone
Keep responses clear and concise (2-3 sentences unless troubleshooting requires more detail).
Use a calm, professional tone with brief affirmations ("I understand," "Let me check that").
Adapt technical depth based on customer responses.
Check for understanding after complex steps: "Does that make sense?"

# Goal
Resolve technical issues through structured troubleshooting:

1. Verify customer identity using email and account ID
2. Identify affected service and severity level
3. Run diagnostics using runSystemDiagnostic tool
4. Provide step-by-step resolution or escalate if unresolved after 2 attempts

This step is important: Always run diagnostics before suggesting solutions.

# Guardrails
Never access customer accounts without identity verification. This step is important.
Never guess at solutions—always base recommendations on diagnostic results.
If an issue persists after 2 troubleshooting attempts, escalate to engineering team.
Acknowledge when you don't know the answer instead of speculating.
```

**PARTIAL EXAMPLE (only first 2 sections discussed):**
```
# Personality
You are a solar sales consultant for SunPower Solutions.
You are professional, persuasive, and focused on helping homeowners understand the benefits of solar energy.
You speak confidently about technical details while keeping explanations accessible to non-technical audiences.

# Environment
You are assisting potential customers via phone calls.
Customers are homeowners who have expressed interest in solar but may have concerns about cost, installation, or ROI.
You have access to pricing calculators, installation scheduling tools, and financing options.
```
(Note: Tone, Goal, etc. are NOT included because they haven't been discussed yet)

**Interview Flow:**
1. Start by asking: "What kind of agent would you like to build today?"
2. Once the user answers, move through the sections one by one (Personality -> Environment -> Tone -> etc.).
3. For each section, ask a specific question to gather the necessary details.
4. After each answer, expand the draft_prompt following the EXACT template patterns above.
5. Always start Personality with "You are a [role]..." format.
6. **CRITICAL: Only include sections in draft_prompt that have been discussed. Do NOT add "(To be discussed)" placeholders. If a section hasn't been covered yet, simply omit it from the draft entirely.**
"""

class PromptChatService:
    def __init__(self, db: Session):
        self.db = db
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def create_session(self) -> PromptChatSession:
        """Start a new chat session."""
        session = PromptChatSession(
            messages=[{"role": "system", "content": SYSTEM_PROMPT}],
            current_step="start"
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        # Generate initial greeting
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        greeting_content = response.choices[0].message.content
        self._append_message(session, "assistant", greeting_content)
        
        return session

    async def add_message(self, session_id: int, content: str) -> Dict[str, Any]:
        """Add user message and get AI response."""
        session = self.db.query(PromptChatSession).filter(PromptChatSession.id == session_id).first()
        if not session:
            raise ValueError("Session not found")
            
        # Add user message
        self._append_message(session, "user", content)
        
        # Get AI response
        messages = [{"role": m["role"], "content": m["content"]} for m in session.messages]
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        ai_response_content = response.choices[0].message.content
        self._append_message(session, "assistant", ai_response_content)
        
        # Parse JSON to return structured response
        try:
            ai_data = json.loads(ai_response_content)
            return {
                "role": "assistant",
                "content": ai_data.get("message", ""),
                "draft_prompt": ai_data.get("draft_prompt", "")
            }
        except json.JSONDecodeError:
            return {
                "role": "assistant",
                "content": ai_response_content
            }

    async def add_message_stream(self, session_id: int, content: str):
        """Add user message and stream AI response."""
        session = self.db.query(PromptChatSession).filter(PromptChatSession.id == session_id).first()
        if not session:
            raise ValueError("Session not found")
            
        # Add user message
        self._append_message(session, "user", content)
        
        # Get AI response with streaming
        messages = [{"role": m["role"], "content": m["content"]} for m in session.messages]
        
        stream = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            response_format={"type": "json_object"},
            stream=True
        )
        
        # Buffer the complete JSON response first
        full_response = ""
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
        
        # Save complete response
        self._append_message(session, "assistant", full_response)
        
        # Parse JSON and stream only the message content
        try:
            ai_data = json.loads(full_response)
            message_content = ai_data.get('message', '')
            draft_prompt = ai_data.get('draft_prompt', '')
            
            # Stream the message content character by character
            for char in message_content:
                yield f"data: {json.dumps({'chunk': char})}\n\n"
            
            # Send final data with draft prompt
            yield f"data: {json.dumps({'done': True, 'message': message_content, 'draft_prompt': draft_prompt})}\n\n"
        except json.JSONDecodeError:
            # Fallback: stream the raw response
            for char in full_response:
                yield f"data: {json.dumps({'chunk': char})}\n\n"
            yield f"data: {json.dumps({'done': True, 'message': full_response, 'draft_prompt': ''})}\n\n"


    async def generate_final_prompt(self, session_id: int) -> GeneratedPrompt:
        """Generate the final system prompt from the conversation."""
        session = self.db.query(PromptChatSession).filter(PromptChatSession.id == session_id).first()
        if not session:
            raise ValueError("Session not found")
            
        # Create generation prompt
        messages = [{"role": m["role"], "content": m["content"]} for m in session.messages]
        messages.append({
            "role": "system", 
            "content": """Based on the interview above, generate the final system prompt for the AI agent.
            Format it clearly with markdown headers (# Personality, # Environment, etc.).
            Ensure all sections discussed are included.
            Do not include any conversational filler, just the raw system prompt."""
        })
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7
        )
        
        final_prompt_text = response.choices[0].message.content
        
        # Create GeneratedPrompt entry
        generated_prompt = GeneratedPrompt(
            source_type=PromptSourceType.CHAT,
            prompt_chat_session_id=session.id,
            prompt_text=final_prompt_text,
            version=1,
            is_active=1,
            llm_config={
                "model": "gpt-4o",
                "temperature": 0.7
            }
        )
        
        session.is_completed = 1
        self.db.add(generated_prompt)
        self.db.commit()
        self.db.refresh(generated_prompt)
        
        return generated_prompt

    def save_prompt(self, session_id: int, draft_prompt: str, name: str = None) -> GeneratedPrompt:
        """Save the current draft prompt without regeneration."""
        session = self.db.query(PromptChatSession).filter(PromptChatSession.id == session_id).first()
        if not session:
            raise ValueError("Session not found")
        
        # Create GeneratedPrompt entry with draft
        generated_prompt = GeneratedPrompt(
            source_type=PromptSourceType.CHAT,
            prompt_chat_session_id=session.id,
            prompt_text=draft_prompt,
            name=name,
            version=1,
            is_active=1,
            llm_config={
                "model": "gpt-4o",
                "temperature": 0.7
            }
        )
        
        session.is_completed = 1
        self.db.add(generated_prompt)
        self.db.commit()
        self.db.refresh(generated_prompt)
        
        return generated_prompt

    def _append_message(self, session: PromptChatSession, role: str, content: str):
        """Helper to append message to session."""
        # SQLAlchemy JSON mutation tracking can be tricky, so we copy, append, and reassign
        messages = list(session.messages)
        messages.append({"role": role, "content": content})
        session.messages = messages
        self.db.commit()
        self.db.refresh(session)
