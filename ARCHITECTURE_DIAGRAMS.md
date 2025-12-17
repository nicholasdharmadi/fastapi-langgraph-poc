# FastAPI LangGraph POC - Architecture Diagrams

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND LAYER (React 18)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │  Dashboard   │  │  Campaigns   │  │    Leads     │  │    Workflows    │ │
│  │     Page     │  │     Page     │  │     Page     │  │      Page       │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────────┘ │
│                                                                               │
│  Components: CampaignCard, LeadTable, StatsCard, ConversationViewer         │
│  State Management: TanStack Query (React Query)                             │
│  Styling: Tailwind CSS + Shadcn/ui                                          │
│  Build Tool: Vite + TypeScript                                              │
└───────────────────────────────────┬───────────────────────────────────────────┘
                                    │ HTTP REST API
                                    │ (axios client)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         API LAYER (FastAPI 0.115)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │  /api/       │  │  /api/       │  │  /api/       │  │  /api/          │ │
│  │  campaigns   │  │  leads       │  │  dashboard   │  │  workflows      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────────┘ │
│                                                                               │
│  Additional: /api/conversations, /api/agents                                │
│  Auto-generated Docs: /docs (Swagger), /redoc                               │
│  CORS: Enabled for localhost development                                    │
└───────────────────┬─────────────────────────────┬───────────────────────────┘
                    │                             │
                    ▼                             ▼
    ┌───────────────────────────┐   ┌───────────────────────────┐
    │   PostgreSQL Database     │   │      Redis Queue          │
    │                           │   │                           │
    │  Tables:                  │   │  RQ (Redis Queue)         │
    │  • campaigns              │   │  Task Broker              │
    │  • leads                  │   │                           │
    │  • campaign_leads         │   └───────────┬───────────────┘
    │  • processing_logs        │               │
    │  • conversation_messages  │               ▼
    │  • agents                 │   ┌───────────────────────────┐
    │  • workflows              │   │      RQ Worker            │
    └───────────────────────────┘   │  (Background Processing)  │
                                    └───────────┬───────────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER (LangGraph 0.2.45)                    │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    LangGraph State Machine                          │    │
│  │                                                                     │    │
│  │  Nodes:                                                            │    │
│  │  • Validate Lead Node    - Validates phone, name, email           │    │
│  │  • SMS Agent Node        - Generates personalized SMS             │    │
│  │  • Voice Agent Node      - Handles voice campaigns                │    │
│  │  • Enrichment Node       - Data enrichment (optional)             │    │
│  │  • Finalize Node         - Saves results, updates stats           │    │
│  │                                                                     │    │
│  │  State: CampaignLeadState (TypedDict)                             │    │
│  │  • campaign_lead_id, campaign_id, lead_id                         │    │
│  │  • lead_data (name, phone, email, company)                        │    │
│  │  • validation_passed, validation_errors                           │    │
│  │  • sms_sent, sms_message, sms_cost                                │    │
│  │  • conversation_history, processing_logs                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    A2A Architecture (Agent-to-Agent)                │    │
│  │                                                                     │    │
│  │  • Creative Agent       - Conversational, engaging messages        │    │
│  │  • Handoff Node         - Context transfer between agents          │    │
│  │  • Deterministic Agent  - Tool execution, structured actions       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    Dynamic Workflow Builder                         │    │
│  │                                                                     │    │
│  │  • Visual workflow editor in frontend                              │    │
│  │  • User-defined nodes and edges                                    │    │
│  │  • Stored as JSON in workflow_config column                        │    │
│  │  • Runtime graph compilation from config                           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────┬───────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES                                    │
│  ┌──────────────────────────┐         ┌──────────────────────────┐          │
│  │      OpenAI API          │         │      LangSmith           │          │
│  │   (GPT-4o-mini)          │         │  (Optional Tracing)      │          │
│  │                          │         │                          │          │
│  │  • Message generation    │         │  • Trace visualization   │          │
│  │  • Token usage tracking  │         │  • Performance metrics   │          │
│  │  • Cost calculation      │         │  • Debugging support     │          │
│  └──────────────────────────┘         └──────────────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Flow Diagram - Campaign Processing Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 1: Campaign Creation                           │
└─────────────────────────────────────────────────────────────────────────────┘

User (Frontend)
    │
    │ 1. Fill campaign form (name, description, agent_type, system_prompt)
    │
    ▼
POST /api/campaigns
    │
    │ 2. FastAPI receives request
    │
    ▼
Create Campaign Record
    │
    ├─► Campaign.status = "draft"
    ├─► Campaign.agent_type = "sms" | "voice" | "both"
    ├─► Campaign.sms_system_prompt = "..."
    └─► Campaign.sms_temperature = 70
    │
    │ 3. Assign N leads to campaign
    │
    ▼
Create CampaignLead Records
    │
    ├─► CampaignLead.campaign_id = campaign.id
    ├─► CampaignLead.lead_id = lead.id
    └─► CampaignLead.status = "pending"
    │
    ▼
Return Campaign to Frontend
    │
    └─► Campaign created successfully (status: draft)


┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 2: Campaign Start                              │
└─────────────────────────────────────────────────────────────────────────────┘

User clicks "Start Campaign"
    │
    ▼
POST /api/campaigns/{id}/start
    │
    │ 1. Update campaign status
    │
    ▼
Campaign.status = "pending"
Campaign.started_at = now()
    │
    │ 2. Enqueue background task
    │
    ▼
RQ Queue.enqueue(process_campaign_task, campaign_id)
    │
    │ 3. Return immediately to user
    │
    ▼
Return 200 OK
    │
    └─► "Campaign started, processing in background"


┌─────────────────────────────────────────────────────────────────────────────┐
│                      PHASE 3: Background Processing                          │
└─────────────────────────────────────────────────────────────────────────────┘

RQ Worker picks up task
    │
    ▼
process_campaign_task(campaign_id)
    │
    │ 1. Update campaign status
    │
    ▼
Campaign.status = "processing"
    │
    │ 2. Get all pending campaign leads
    │
    ▼
campaign_leads = CampaignLead.filter(
    campaign_id=campaign_id,
    status="pending"
)
    │
    │ 3. Process each lead sequentially
    │
    ▼
For each campaign_lead:
    │
    ├─► process_campaign_lead_with_graph(campaign_lead.id, db)
    │       │
    │       └─► See PHASE 4 below
    │
    ▼
All leads processed
    │
    │ 4. Update campaign status
    │
    ▼
Campaign.status = "completed"
Campaign.completed_at = now()


┌─────────────────────────────────────────────────────────────────────────────┐
│                   PHASE 4: LangGraph Workflow Execution                      │
└─────────────────────────────────────────────────────────────────────────────┘

process_campaign_lead_with_graph(campaign_lead_id)
    │
    │ 1. Fetch campaign lead with relationships
    │
    ▼
campaign_lead = db.query(CampaignLead).get(campaign_lead_id)
campaign = campaign_lead.campaign
lead = campaign_lead.lead
    │
    │ 2. Initialize LangGraph state
    │
    ▼
initial_state = {
    'campaign_lead_id': str(campaign_lead.id),
    'lead_data': {
        'name': lead.name,
        'phone': lead.phone,
        'email': lead.email,
        'company': lead.company
    },
    'agent_type': campaign.agent_type,
    'sms_system_prompt': campaign.sms_system_prompt,
    'sms_temperature': campaign.sms_temperature / 100.0,
    'validation_passed': False,
    'sms_sent': False,
    'conversation_history': [],
    'processing_logs': []
}
    │
    │ 3. Create and compile LangGraph workflow
    │
    ▼
graph = create_campaign_lead_graph()  # or A2A or Dynamic
    │
    │ 4. Execute workflow
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LangGraph State Machine                              │
│                                                                               │
│  START                                                                        │
│    │                                                                          │
│    ▼                                                                          │
│  ┌──────────────────────┐                                                    │
│  │  Validate Lead Node  │                                                    │
│  │                      │                                                    │
│  │  • Check phone       │                                                    │
│  │  • Check name        │                                                    │
│  │  • Validate format   │                                                    │
│  └──────────┬───────────┘                                                    │
│             │                                                                 │
│        ┌────┴─────┐                                                          │
│        │          │                                                           │
│     FAILED     PASSED                                                         │
│        │          │                                                           │
│        │          ▼                                                           │
│        │    ┌──────────────────────┐                                         │
│        │    │   SMS Agent Node     │                                         │
│        │    │                      │                                         │
│        │    │  1. Build prompt:    │                                         │
│        │    │     System: {prompt} │                                         │
│        │    │     User: "Generate  │                                         │
│        │    │      SMS for {name}" │                                         │
│        │    │                      │                                         │
│        │    │  2. Call OpenAI:     │                                         │
│        │    │     model=gpt-4o-mini│                                         │
│        │    │     temp=0.7         │                                         │
│        │    │                      │                                         │
│        │    │  3. Get response:    │                                         │
│        │    │     message = "..."  │                                         │
│        │    │     tokens = 150     │                                         │
│        │    │     cost = $0.0002   │                                         │
│        │    │                      │                                         │
│        │    │  4. Send SMS (mock)  │                                         │
│        │    └──────────┬───────────┘                                         │
│        │               │                                                      │
│        │          ┌────┴─────┐                                               │
│        │          │          │                                                │
│        │     agent_type   agent_type                                         │
│        │      = "both"    = "sms"                                            │
│        │          │          │                                                │
│        │          ▼          │                                                │
│        │    ┌──────────────────────┐                                         │
│        │    │  Voice Agent Node    │                                         │
│        │    │  (optional)          │                                         │
│        │    └──────────┬───────────┘                                         │
│        │               │                                                      │
│        └───────────────┼───────────┘                                         │
│                        │                                                      │
│                        ▼                                                      │
│                  ┌──────────────────────┐                                    │
│                  │   Finalize Node      │                                    │
│                  │                      │                                    │
│                  │  • Set final status  │                                    │
│                  │  • Save logs         │                                    │
│                  │  • Update stats      │                                    │
│                  └──────────┬───────────┘                                    │
│                             │                                                 │
│                             ▼                                                 │
│                           END                                                 │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    │ 5. Get final state
    │
    ▼
final_state = {
    'status': 'completed' | 'failed',
    'sms_sent': True | False,
    'sms_message': "Hi John, ...",
    'sms_cost': 0.0002,
    'conversation_history': [
        {'role': 'system', 'content': '...'},
        {'role': 'user', 'content': '...'},
        {'role': 'assistant', 'content': '...'}
    ],
    'processing_logs': [
        {'node': 'validate', 'message': 'Lead validated'},
        {'node': 'sms_agent', 'message': 'SMS generated'}
    ],
    'error_message': '' | 'Error details'
}


┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 5: Results Storage                             │
└─────────────────────────────────────────────────────────────────────────────┘

    │ 1. Update CampaignLead record
    │
    ▼
CampaignLead.status = final_state['status']
CampaignLead.sms_sent = final_state['sms_sent']
CampaignLead.sms_message = final_state['sms_message']
CampaignLead.error_message = final_state['error_message']
CampaignLead.trace_id = final_state['trace_id']
CampaignLead.processed_at = now()
    │
    │ 2. Save conversation messages
    │
    ▼
For each msg in final_state['conversation_history']:
    ConversationMessage.create(
        campaign_lead_id=campaign_lead.id,
        role=msg['role'],
        content=msg['content'],
        message_metadata=msg.get('metadata', {})
    )
    │
    │ 3. Save processing logs
    │
    ▼
For each log in final_state['processing_logs']:
    ProcessingLog.create(
        campaign_lead_id=campaign_lead.id,
        level='INFO' | 'ERROR',
        node_name=log['node'],
        message=log['message'],
        log_metadata=log
    )
    │
    │ 4. Update campaign statistics
    │
    ▼
Campaign.update_stats()
    │
    ├─► stats.total_leads = count(campaign_leads)
    ├─► stats.pending = count(status='pending')
    ├─► stats.processing = count(status='processing')
    ├─► stats.completed = count(status='completed')
    ├─► stats.failed = count(status='failed')
    ├─► stats.sms_sent = count(sms_sent=True)
    └─► stats.success_rate = (completed / total) * 100


┌─────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 6: Frontend Display                             │
└─────────────────────────────────────────────────────────────────────────────┘

Frontend (React Query)
    │
    │ 1. Poll campaign endpoint every 5 seconds
    │
    ▼
GET /api/campaigns/{id}
    │
    │ 2. Receive updated campaign data
    │
    ▼
{
    "id": 1,
    "name": "Q1 Outreach",
    "status": "processing" | "completed",
    "stats": {
        "total_leads": 100,
        "pending": 20,
        "processing": 5,
        "completed": 70,
        "failed": 5,
        "sms_sent": 70,
        "success_rate": 70.0
    }
}
    │
    │ 3. Display in UI
    │
    ▼
Dashboard shows:
    • Progress bar (70/100 completed)
    • Success rate (70%)
    • Real-time status updates
    │
    │ 4. User clicks "View Details"
    │
    ▼
GET /api/campaigns/{id}/logs
    │
    ▼
Display processing logs:
    • [INFO] validate: Lead validated
    • [INFO] sms_agent: SMS generated successfully
    • [INFO] finalize: Processing complete
    │
    │ 5. User clicks "View Conversation"
    │
    ▼
GET /api/conversations/{campaign_lead_id}
    │
    ▼
Display conversation history:
    • System: "You are a sales assistant..."
    • User: "Generate SMS for John Doe"
    • Assistant: "Hi John, I wanted to reach out..."
```

---

## 3. Component Diagram (UML-Style)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND COMPONENTS                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────┐
│   «page»                 │
│   DashboardPage          │
├──────────────────────────┤
│ + useQuery()             │
│ + fetchStats()           │
│ + render()               │
└────────┬─────────────────┘
         │ uses
         ▼
┌──────────────────────────┐
│   «component»            │
│   StatsCard              │
├──────────────────────────┤
│ + props: StatsData       │
│ + render()               │
└──────────────────────────┘

┌──────────────────────────┐
│   «page»                 │
│   CampaignsPage          │
├──────────────────────────┤
│ + useQuery()             │
│ + fetchCampaigns()       │
│ + createCampaign()       │
│ + render()               │
└────────┬─────────────────┘
         │ uses
         ▼
┌──────────────────────────┐
│   «component»            │
│   CampaignCard           │
├──────────────────────────┤
│ + props: Campaign        │
│ + onStart()              │
│ + onDelete()             │
│ + render()               │
└──────────────────────────┘

┌──────────────────────────┐
│   «page»                 │
│   CampaignDetailPage     │
├──────────────────────────┤
│ + useQuery()             │
│ + fetchCampaign()        │
│ + fetchLogs()            │
│ + render()               │
└────────┬─────────────────┘
         │ uses
         ▼
┌──────────────────────────┐
│   «component»            │
│   ConversationViewer     │
├──────────────────────────┤
│ + props: campaign_lead_id│
│ + fetchMessages()        │
│ + render()               │
└──────────────────────────┘

┌──────────────────────────┐
│   «page»                 │
│   WorkflowsPage          │
├──────────────────────────┤
│ + useReactFlow()         │
│ + saveWorkflow()         │
│ + render()               │
└────────┬─────────────────┘
         │ uses
         ▼
┌──────────────────────────┐
│   «component»            │
│   WorkflowBuilder        │
├──────────────────────────┤
│ + nodes: Node[]          │
│ + edges: Edge[]          │
│ + onNodesChange()        │
│ + onEdgesChange()        │
│ + render()               │
└──────────────────────────┘

┌──────────────────────────┐
│   «service»              │
│   api.ts                 │
├──────────────────────────┤
│ + getCampaigns()         │
│ + createCampaign()       │
│ + startCampaign()        │
│ + getLeads()             │
│ + getConversations()     │
└──────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                              BACKEND COMPONENTS                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────┐
│   «controller»           │
│   campaigns.py           │
├──────────────────────────┤
│ + get_campaigns()        │
│ + create_campaign()      │
│ + start_campaign()       │
│ + get_campaign_logs()    │
└────────┬─────────────────┘
         │ uses
         ▼
┌──────────────────────────┐
│   «model»                │
│   Campaign               │
├──────────────────────────┤
│ + id: int                │
│ + name: str              │
│ + status: CampaignStatus │
│ + agent_type: AgentType  │
│ + stats: dict            │
│ + update_stats()         │
└──────────────────────────┘

┌──────────────────────────┐
│   «controller»           │
│   leads.py               │
├──────────────────────────┤
│ + get_leads()            │
│ + create_lead()          │
│ + update_lead()          │
└────────┬─────────────────┘
         │ uses
         ▼
┌──────────────────────────┐
│   «model»                │
│   Lead                   │
├──────────────────────────┤
│ + id: int                │
│ + name: str              │
│ + phone: str             │
│ + email: str             │
│ + company: str           │
└──────────────────────────┘

┌──────────────────────────┐
│   «controller»           │
│   conversations.py       │
├──────────────────────────┤
│ + get_messages()         │
│ + create_message()       │
└────────┬─────────────────┘
         │ uses
         ▼
┌──────────────────────────┐
│   «model»                │
│   ConversationMessage    │
├──────────────────────────┤
│ + id: int                │
│ + campaign_lead_id: int  │
│ + role: str              │
│ + content: str           │
│ + message_metadata: dict │
└──────────────────────────┘

┌──────────────────────────┐
│   «service»              │
│   campaign_tasks.py      │
├──────────────────────────┤
│ + process_campaign_task()│
└────────┬─────────────────┘
         │ uses
         ▼
┌──────────────────────────┐
│   «orchestrator»         │
│   graph.py               │
├──────────────────────────┤
│ + create_campaign_lead_  │
│   graph()                │
│ + create_a2a_campaign_   │
│   lead_graph()           │
│ + create_dynamic_        │
│   campaign_lead_graph()  │
│ + process_campaign_lead_ │
│   with_graph()           │
│ + initialize_lead_state()│
└────────┬─────────────────┘
         │ uses
         ▼
┌──────────────────────────┐
│   «orchestrator»         │
│   nodes.py               │
├──────────────────────────┤
│ + validate_lead_node()   │
│ + sms_agent_node()       │
│ + voice_agent_node()     │
│ + enrichment_node()      │
│ + finalize_node()        │
│ + route_after_validation│
│ + route_after_sms()      │
└────────┬─────────────────┘
         │ uses
         ▼
┌──────────────────────────┐
│   «service»              │
│   openai_service.py      │
├──────────────────────────┤
│ + generate_sms_message() │
│ + calculate_cost()       │
└──────────────────────────┘

┌──────────────────────────┐
│   «orchestrator»         │
│   a2a_nodes.py           │
├──────────────────────────┤
│ + a2a_creative_agent_    │
│   node()                 │
│ + a2a_deterministic_     │
│   agent_node()           │
│ + a2a_handoff_node()     │
│ + route_a2a_workflow()   │
└──────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATABASE SCHEMA                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────┐
│   campaigns              │
├──────────────────────────┤
│ PK id                    │
│    name                  │
│    description           │
│    agent_type            │
│    status                │
│    sms_system_prompt     │
│    sms_temperature       │
│    workflow_config       │
│    stats                 │
│ FK agent_id              │
│ FK creative_agent_id     │
│ FK deterministic_agent_id│
│    created_at            │
│    updated_at            │
│    started_at            │
│    completed_at          │
└────────┬─────────────────┘
         │ 1:N
         ▼
┌──────────────────────────┐
│   campaign_leads         │
├──────────────────────────┤
│ PK id                    │
│ FK campaign_id           │
│ FK lead_id               │
│    status                │
│    sms_sent              │
│    sms_message           │
│    sms_response          │
│    voice_call_made       │
│    trace_id              │
│    error_message         │
│    created_at            │
│    updated_at            │
│    processed_at          │
└────────┬─────────────────┘
         │ 1:N
         ▼
┌──────────────────────────┐
│   conversation_messages  │
├──────────────────────────┤
│ PK id                    │
│ FK campaign_lead_id      │
│    role                  │
│    content               │
│    message_metadata      │
│    created_at            │
└──────────────────────────┘

┌──────────────────────────┐
│   processing_logs        │
├──────────────────────────┤
│ PK id                    │
│ FK campaign_lead_id      │
│    level                 │
│    node_name             │
│    message               │
│    log_metadata          │
│    created_at            │
└──────────────────────────┘

┌──────────────────────────┐
│   leads                  │
├──────────────────────────┤
│ PK id                    │
│    name                  │
│    phone                 │
│    email                 │
│    company               │
│    notes                 │
│    created_at            │
│    updated_at            │
└──────────────────────────┘

┌──────────────────────────┐
│   agents                 │
├──────────────────────────┤
│ PK id                    │
│    name                  │
│    system_prompt         │
│    model                 │
│    tools                 │
│    created_at            │
│    updated_at            │
└──────────────────────────┘

┌──────────────────────────┐
│   workflows              │
├──────────────────────────┤
│ PK id                    │
│    name                  │
│    config                │
│    created_at            │
│    updated_at            │
└──────────────────────────┘
```

---

## 4. LangGraph Workflow State Machine

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STANDARD WORKFLOW                                    │
└─────────────────────────────────────────────────────────────────────────────┘

    ●  START
    │
    ▼
┌─────────────────────┐
│  Validate Lead      │
│  Node               │
│                     │
│  Checks:            │
│  • phone is valid   │
│  • name is present  │
│  • email format OK  │
└──────┬──────────────┘
       │
       ▼
    ╱     ╲
   ╱ Valid? ╲
   ╲       ╱
    ╲     ╱
     ╲   ╱
      │ │
  NO  │ │  YES
      │ │
      │ └──────────────────┐
      │                    │
      │                    ▼
      │            ┌─────────────────────┐
      │            │  SMS Agent Node     │
      │            │                     │
      │            │  Actions:           │
      │            │  1. Build prompt    │
      │            │  2. Call OpenAI     │
      │            │  3. Get response    │
      │            │  4. Calculate cost  │
      │            │  5. Send SMS (mock) │
      │            └──────┬──────────────┘
      │                   │
      │                   ▼
      │                ╱     ╲
      │               ╱ Agent  ╲
      │               ╲ Type?  ╱
      │                ╲     ╱
      │                 ╲   ╱
      │              SMS │ │ BOTH
      │                  │ │
      │                  │ └──────────────┐
      │                  │                │
      │                  │                ▼
      │                  │        ┌─────────────────────┐
      │                  │        │  Voice Agent Node   │
      │                  │        │                     │
      │                  │        │  Actions:           │
      │                  │        │  1. Generate script │
      │                  │        │  2. Make call       │
      │                  │        │  3. Track duration  │
      │                  │        └──────┬──────────────┘
      │                  │               │
      └──────────────────┼───────────────┘
                         │
                         ▼
                 ┌─────────────────────┐
                 │  Finalize Node      │
                 │                     │
                 │  Actions:           │
                 │  1. Set status      │
                 │  2. Save logs       │
                 │  3. Update stats    │
                 │  4. Store results   │
                 └──────┬──────────────┘
                        │
                        ▼
                        ●  END


┌─────────────────────────────────────────────────────────────────────────────┐
│                         A2A ARCHITECTURE WORKFLOW                            │
└─────────────────────────────────────────────────────────────────────────────┘

    ●  START
    │
    ▼
┌─────────────────────┐
│  Validate Lead      │
│  Node               │
└──────┬──────────────┘
       │
       ▼
    ╱     ╲
   ╱ Valid? ╲
   ╲       ╱
    ╲     ╱
     ╲   ╱
  NO  │ │  YES
      │ │
      │ └──────────────────┐
      │                    │
      │                    ▼
      │            ┌─────────────────────┐
      │            │  Creative Agent     │
      │            │  Node               │
      │            │                     │
      │            │  Purpose:           │
      │            │  • Conversational   │
      │            │  • Engaging         │
      │            │  • Personalized     │
      │            │                     │
      │            │  Output:            │
      │            │  • Draft message    │
      │            │  • Conversation ctx │
      │            └──────┬──────────────┘
      │                   │
      │                   ▼
      │            ┌─────────────────────┐
      │            │  Handoff Node       │
      │            │                     │
      │            │  Actions:           │
      │            │  • Transfer context │
      │            │  • Prepare state    │
      │            │  • Log handoff      │
      │            └──────┬──────────────┘
      │                   │
      │                   ▼
      │            ┌─────────────────────┐
      │            │  Deterministic      │
      │            │  Agent Node         │
      │            │                     │
      │            │  Purpose:           │
      │            │  • Tool execution   │
      │            │  • Structured tasks │
      │            │  • Data validation  │
      │            │                     │
      │            │  Output:            │
      │            │  • Final message    │
      │            │  • Tool results     │
      │            └──────┬──────────────┘
      │                   │
      └───────────────────┘
                          │
                          ▼
                  ┌─────────────────────┐
                  │  Finalize Node      │
                  └──────┬──────────────┘
                         │
                         ▼
                         ●  END


┌─────────────────────────────────────────────────────────────────────────────┐
│                         DYNAMIC WORKFLOW (User-Configured)                   │
└─────────────────────────────────────────────────────────────────────────────┘

    ●  START
    │
    │  User drags and drops nodes in visual editor
    │  Nodes can include:
    │  • Validate Lead
    │  • SMS Agent
    │  • Voice Agent
    │  • Enrichment (data lookup)
    │  • Custom nodes
    │
    ▼
┌─────────────────────┐
│  User-Defined       │
│  Node 1             │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  User-Defined       │
│  Node 2             │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  User-Defined       │
│  Node N             │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Finalize Node      │
│  (always last)      │
└──────┬──────────────┘
       │
       ▼
       ●  END

Configuration stored as JSON:
{
  "nodes": [
    {"id": "1", "type": "validate", "data": {"label": "Validate"}},
    {"id": "2", "type": "sms", "data": {"label": "SMS Agent"}},
    {"id": "3", "type": "finalize", "data": {"label": "Finalize"}}
  ],
  "edges": [
    {"source": "1", "target": "2"},
    {"source": "2", "target": "3"}
  ]
}
```

---

## 5. Deployment Architecture (Docker Compose)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DOCKER COMPOSE SERVICES                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────┐
│   Frontend Container     │
│   (langgraph-frontend)   │
├──────────────────────────┤
│  Image: Node 18          │
│  Port: 3000:3000         │
│  Command: npm run dev    │
│  Volumes:                │
│    ./frontend:/app       │
│  Env:                    │
│    VITE_API_URL=/api     │
└────────┬─────────────────┘
         │ HTTP
         │ /api/* → backend:8000
         ▼
┌──────────────────────────┐
│   Backend Container      │
│   (langgraph-backend)    │
├──────────────────────────┤
│  Image: Python 3.11      │
│  Port: 8001:8000         │
│  Command: uvicorn        │
│  Volumes:                │
│    ./backend:/app        │
│  Env:                    │
│    DATABASE_URL          │
│    REDIS_URL             │
│    OPENAI_API_KEY        │
└────────┬─────────────────┘
         │
         ├──────────────────┐
         │                  │
         ▼                  ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│   PostgreSQL Container   │  │   Redis Container        │
│   (langgraph-postgres)   │  │   (langgraph-redis)      │
├──────────────────────────┤  ├──────────────────────────┤
│  Image: postgres:16      │  │  Image: redis:7          │
│  Port: 5432:5432         │  │  Port: 6380:6379         │
│  Volume:                 │  │  Healthcheck:            │
│    postgres_data:/var/   │  │    redis-cli ping        │
│    lib/postgresql/data   │  └────────┬─────────────────┘
│  Healthcheck:            │           │
│    pg_isready            │           │ RQ Queue
└──────────────────────────┘           │
                                       ▼
                           ┌──────────────────────────┐
                           │   Worker Container       │
                           │   (langgraph-worker)     │
                           ├──────────────────────────┤
                           │  Image: Python 3.11      │
                           │  Command: python worker.py│
                           │  Volumes:                │
                           │    ./backend:/app        │
                           │  Env:                    │
                           │    DATABASE_URL          │
                           │    REDIS_URL             │
                           │    OPENAI_API_KEY        │
                           └──────────────────────────┘

Service Dependencies:
• Frontend depends on Backend
• Backend depends on PostgreSQL + Redis
• Worker depends on PostgreSQL + Redis

Health Checks:
• PostgreSQL: pg_isready -U postgres
• Redis: redis-cli ping
• Backend: GET /health (implicit)
```

---

## 6. Key Design Patterns

### 1. **State Machine Pattern** (LangGraph)

- Declarative workflow definition
- Immutable state transitions
- Conditional routing based on state
- Error handling at each node

### 2. **Repository Pattern** (Database Access)

- SQLAlchemy ORM models
- Separation of data access from business logic
- Async database operations

### 3. **Service Layer Pattern**

- `openai_service.py` - External API integration
- `sms_service.py` - SMS sending abstraction
- Decoupled from controllers

### 4. **Background Job Pattern** (RQ)

- Async task processing
- Queue-based architecture
- Retry mechanism
- Job status tracking

### 5. **API Gateway Pattern** (FastAPI)

- Single entry point for frontend
- Auto-generated documentation
- Request/response validation
- CORS handling

### 6. **Observer Pattern** (React Query)

- Automatic cache invalidation
- Optimistic updates
- Background refetching
- Real-time UI updates

---

## 7. Technology Decisions

| Decision                     | Rationale                                                       |
| ---------------------------- | --------------------------------------------------------------- |
| **FastAPI over Django**      | Native async support, auto-generated docs, better performance   |
| **LangGraph over LangChain** | State machine abstraction, visual workflows, easier debugging   |
| **RQ over Celery**           | Simpler setup for POC, fewer dependencies, easier to understand |
| **PostgreSQL**               | Production-ready, JSONB support, good SQLAlchemy integration    |
| **React Query**              | Automatic caching, background refetching, optimistic updates    |
| **Vite over CRA**            | Faster builds, better DX, native ESM support                    |
| **Shadcn/ui**                | Accessible components, customizable, Tailwind-based             |

---

## Summary

This architecture demonstrates a modern, scalable approach to building AI-powered campaign platforms:

1. **Frontend**: React 18 + TypeScript + Vite for fast, type-safe UI development
2. **Backend**: FastAPI for high-performance async API with auto-generated docs
3. **Orchestration**: LangGraph for declarative, visual workflow management
4. **Background Processing**: RQ + Redis for reliable async task execution
5. **Database**: PostgreSQL for robust data storage with JSONB support
6. **AI Integration**: OpenAI GPT-4o-mini for intelligent message generation
7. **Monitoring**: LangSmith for optional tracing and debugging

The architecture supports three workflow modes:

- **Standard**: Pre-defined SMS/Voice workflows
- **A2A**: Agent-to-Agent handoff for complex conversations
- **Dynamic**: User-configured visual workflows

All components are containerized with Docker Compose for easy local development and deployment.
