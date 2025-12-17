# A2A (Agent-to-Agent) Architecture

## Overview

The A2A architecture introduces a dual-agent system where campaigns utilize two specialized agents working in tandem:

1. **Creative Agent** - Handles conversation, message generation, personalization, and context management
2. **Deterministic Agent** - Handles tool execution, API integrations, SMS/voice delivery, and structured operations

This separation of concerns improves:

- **Specialization**: Each agent focuses on what it does best
- **Flexibility**: Different models/prompts can be used for each role
- **Reliability**: Deterministic operations are isolated from creative generation
- **Cost Optimization**: Use expensive models for creativity, cheaper ones for execution

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Campaign Execution                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐                                           │
│  │  Validate    │                                           │
│  │  Lead        │                                           │
│  └──────┬───────┘                                           │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────────────────────────────────────┐           │
│  │         Creative Agent (GPT-4o)             │           │
│  │  • Generate personalized message            │           │
│  │  • Consider lead context & enrichment       │           │
│  │  • Maintain conversation flow               │           │
│  │  • Apply brand voice & tone                 │           │
│  └─────────────────┬───────────────────────────┘           │
│                    │                                         │
│                    ▼                                         │
│  ┌─────────────────────────────────────────────┐           │
│  │              Handoff Node                   │           │
│  │  • Coordinate between agents                │           │
│  │  • Pass context & state                     │           │
│  └─────────────────┬───────────────────────────┘           │
│                    │                                         │
│                    ▼                                         │
│  ┌─────────────────────────────────────────────┐           │
│  │    Deterministic Agent (GPT-4o-mini)        │           │
│  │  • Execute send_sms tool                    │           │
│  │  • Make API calls                           │           │
│  │  • Handle voice calls                       │           │
│  │  • Update CRM systems                       │           │
│  └─────────────────┬───────────────────────────┘           │
│                    │                                         │
│                    ▼                                         │
│  ┌──────────────┐                                           │
│  │  Finalize    │                                           │
│  │  & Report    │                                           │
│  └──────────────┘                                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Data Model

### Agent Model

```python
class AgentRole(str, enum.Enum):
    CREATIVE = "creative"         # Message generation & conversation
    DETERMINISTIC = "deterministic"  # Tool execution & APIs
    HYBRID = "hybrid"             # Both (backward compatible)

class Agent:
    id: int
    name: str
    description: str
    system_prompt: str
    model: str  # e.g., "gpt-4o", "gpt-4o-mini"
    role: AgentRole
    capabilities: List[str]  # ["sms", "voice", "email"]
    tools: List[Dict]  # Tool configurations
```

### Campaign Model (Extended)

```python
class Campaign:
    # ... existing fields ...

    # Legacy single agent (backward compatible)
    agent_id: int
    agent: Agent

    # A2A dual agents
    creative_agent_id: int
    creative_agent: Agent
    deterministic_agent_id: int
    deterministic_agent: Agent
```

### State (Extended)

```python
class CampaignLeadState:
    # ... existing fields ...

    # A2A configuration
    use_a2a: bool
    creative_agent_id: str
    creative_agent_prompt: str
    creative_agent_model: str
    deterministic_agent_id: str
    deterministic_agent_prompt: str
    deterministic_agent_model: str
    deterministic_agent_tools: List[Dict]
```

## Workflow

### 1. Campaign Creation with A2A

```python
# Create campaign with A2A agents
campaign = Campaign(
    name="Q1 Outreach",
    agent_type=AgentType.SMS,
    creative_agent_id=1,      # Creative agent
    deterministic_agent_id=2,  # Deterministic agent
    # ... other fields
)
```

### 2. Lead Processing Flow

```
1. Validate Lead
   ↓
2. Creative Agent Node
   - Receives lead data + enrichment
   - Generates personalized message
   - Stores in state['sms_message']
   ↓
3. Handoff Node
   - Coordinates agent transition
   - Passes context
   ↓
4. Deterministic Agent Node
   - Receives message from creative agent
   - Executes send_sms tool
   - Handles API integrations
   - Updates delivery status
   ↓
5. Finalize
   - Aggregates results
   - Updates campaign stats
```

### 3. Conversation History

Both agents contribute to a shared conversation history:

```python
conversation_history = [
    {
        'role': 'system',
        'agent': 'creative',
        'content': 'System prompt...'
    },
    {
        'role': 'assistant',
        'agent': 'creative',
        'content': 'Generated message...',
        'metadata': {'cost': 0.002, 'model': 'gpt-4o'}
    },
    {
        'role': 'tool',
        'agent': 'deterministic',
        'content': 'SMS sent to +1234567890',
        'metadata': {'tool': 'send_sms', 'success': True}
    }
]
```

## Implementation Guide

### Step 1: Create A2A Agents

```bash
# Run migration to add A2A schema
cd backend
python scripts/migrate_a2a.py
```

This creates:

- Schema changes (role, creative_agent_id, deterministic_agent_id)
- Two example agents (Creative & Deterministic)

### Step 2: Create A2A Campaign

Via API:

```bash
POST /api/campaigns
{
  "name": "A2A Test Campaign",
  "agent_type": "sms",
  "creative_agent_id": 1,
  "deterministic_agent_id": 2,
  "lead_ids": [1, 2, 3]
}
```

### Step 3: Run Campaign

```bash
POST /api/campaigns/{id}/start
```

The system automatically detects A2A configuration and uses the dual-agent workflow.

## Agent Configuration Examples

### Creative Agent

```python
Agent(
    name="Creative Sales Agent",
    role=AgentRole.CREATIVE,
    model="gpt-4o",  # More capable model for creativity
    system_prompt="""You are a creative sales assistant.
    Craft personalized, engaging messages that:
    - Feel human and authentic
    - Adapt to lead context
    - Maintain professional tone
    - Drive action""",
    capabilities=["sms", "email"],
    tools=[]  # No tools, focus on generation
)
```

### Deterministic Agent

```python
Agent(
    name="Execution Agent",
    role=AgentRole.DETERMINISTIC,
    model="gpt-4o-mini",  # Cheaper model for execution
    system_prompt="""You are a deterministic assistant.
    Execute tools accurately and reliably:
    - Send SMS/emails
    - Make API calls
    - Update systems
    - Handle errors gracefully""",
    capabilities=["sms", "voice", "api"],
    tools=[
        {"name": "send_sms", "config": {"provider": "twilio"}},
        {"name": "make_call", "config": {"provider": "livekit"}},
        {"name": "update_crm", "config": {"provider": "salesforce"}}
    ]
)
```

## Benefits

### 1. Specialization

- Creative agent focuses on quality messaging
- Deterministic agent focuses on reliable execution
- Each can be optimized independently

### 2. Cost Optimization

- Use GPT-4o for creative tasks (where quality matters)
- Use GPT-4o-mini for execution (where reliability matters)
- Reduce overall costs by 60-80%

### 3. Flexibility

- Swap creative agents for different campaigns
- Use different models per agent
- A/B test creative approaches
- Maintain consistent execution

### 4. Reliability

- Separate concerns reduce failure points
- Deterministic agent handles retries
- Creative agent focuses on quality
- Better error handling

### 5. Observability

- Track which agent performed which action
- Separate cost tracking per agent
- Clear conversation flow
- Better debugging

## Backward Compatibility

The system maintains full backward compatibility:

1. **Legacy campaigns** (with `agent_id`) continue to work
2. **Hybrid agents** can handle both roles
3. **Automatic detection** of A2A vs legacy mode
4. **Gradual migration** - no breaking changes

## API Endpoints

### Create A2A Campaign

```http
POST /api/campaigns
Content-Type: application/json

{
  "name": "A2A Campaign",
  "description": "Using dual agents",
  "agent_type": "sms",
  "creative_agent_id": 1,
  "deterministic_agent_id": 2,
  "lead_ids": [1, 2, 3]
}
```

### List Agents by Role

```http
GET /api/agents?role=creative
GET /api/agents?role=deterministic
```

### View Campaign A2A Configuration

```http
GET /api/campaigns/{id}

Response:
{
  "id": 1,
  "name": "A2A Campaign",
  "creative_agent": {
    "id": 1,
    "name": "Creative Sales Agent",
    "role": "creative",
    "model": "gpt-4o"
  },
  "deterministic_agent": {
    "id": 2,
    "name": "Execution Agent",
    "role": "deterministic",
    "model": "gpt-4o-mini"
  }
}
```

## Monitoring & Debugging

### Conversation Logs

View the full A2A conversation flow:

```http
GET /api/campaigns/{id}/conversation/{lead_id}

Response:
[
  {
    "role": "assistant",
    "agent": "creative",
    "agent_id": 1,
    "content": "Hi John! Noticed you're in tech...",
    "metadata": {
      "cost": 0.002,
      "model": "gpt-4o"
    }
  },
  {
    "role": "tool",
    "agent": "deterministic",
    "agent_id": 2,
    "content": "SMS sent successfully",
    "metadata": {
      "tool": "send_sms",
      "success": true
    }
  }
]
```

### Processing Logs

Track agent handoffs:

```http
GET /api/campaigns/{id}/logs

Response:
[
  {
    "node": "a2a_creative_agent",
    "message": "Creative agent generated message",
    "timestamp": "2025-11-27T22:00:00Z"
  },
  {
    "node": "a2a_handoff",
    "message": "Agent handoff coordination",
    "timestamp": "2025-11-27T22:00:01Z"
  },
  {
    "node": "a2a_deterministic_agent",
    "message": "SMS sent",
    "timestamp": "2025-11-27T22:00:02Z"
  }
]
```

## Future Enhancements

1. **Multi-turn conversations** - Creative agent handles back-and-forth
2. **Dynamic tool selection** - Deterministic agent chooses tools
3. **Agent marketplace** - Share/discover specialized agents
4. **A/B testing** - Compare creative agents automatically
5. **Real-time handoff** - Stream agent transitions to UI
6. **Agent analytics** - Performance metrics per agent

## Migration Path

### For Existing Campaigns

1. Run migration: `python scripts/migrate_a2a.py`
2. Existing campaigns continue with `agent_id`
3. New campaigns can use A2A
4. Gradually migrate campaigns to A2A

### For New Projects

1. Start with A2A from day one
2. Create creative & deterministic agents
3. All campaigns use dual-agent approach
4. Ignore legacy `agent_id` field

---
