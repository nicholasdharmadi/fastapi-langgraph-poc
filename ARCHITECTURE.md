# Architecture Documentation

## System Overview

This POC demonstrates a modern SMS campaign management system using FastAPI, LangChain, and LangGraph.

## Technology Stack

### Backend
- **FastAPI 0.115.0** - Modern Python web framework with automatic API docs
- **SQLAlchemy 2.0** - ORM for database operations
- **PostgreSQL** - Production-ready relational database
- **Redis + RQ** - Background task queue
- **LangChain 0.3.7** - AI agent framework
- **LangGraph 0.2.45** - State machine orchestration
- **OpenAI GPT-4o-mini** - SMS message generation

### Frontend
- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool
- **TailwindCSS** - Utility-first CSS
- **React Query** - Data fetching and caching
- **React Router** - Client-side routing

## Project Structure

```
fastapi-langgraph-poc/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # Database setup
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── campaign.py
│   │   │   ├── lead.py
│   │   │   ├── campaign_lead.py
│   │   │   └── processing_log.py
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── campaign.py
│   │   │   ├── lead.py
│   │   │   └── ...
│   │   ├── api/                 # API endpoints
│   │   │   ├── campaigns.py
│   │   │   ├── leads.py
│   │   │   └── dashboard.py
│   │   ├── services/            # External services
│   │   │   ├── openai_service.py
│   │   │   └── sms_service.py
│   │   ├── orchestrator/        # LangGraph workflows
│   │   │   ├── state.py
│   │   │   ├── nodes.py
│   │   │   └── graph.py
│   │   └── tasks/               # Background tasks
│   │       └── campaign_tasks.py
│   ├── worker.py                # RQ worker
│   ├── seed_data.py             # Sample data
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Main app component
│   │   ├── main.tsx             # Entry point
│   │   ├── pages/               # Page components
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── CampaignsPage.tsx
│   │   │   ├── CampaignDetailPage.tsx
│   │   │   └── LeadsPage.tsx
│   │   ├── services/            # API client
│   │   │   └── api.ts
│   │   ├── types/               # TypeScript types
│   │   │   └── index.ts
│   │   └── lib/                 # Utilities
│   │       └── utils.ts
│   ├── package.json
│   └── vite.config.ts
│
├── README.md
├── ARCHITECTURE.md
└── quickstart.sh
```

## Data Flow

### Campaign Creation Flow

```
User (Frontend)
    │
    ├─► POST /api/campaigns
    │       │
    │       ├─► Create Campaign record
    │       ├─► Assign N leads
    │       └─► Create CampaignLead records
    │
    └─► Campaign created (status: draft)
```

### Campaign Processing Flow

```
User clicks "Start"
    │
    ├─► POST /api/campaigns/{id}/start
    │       │
    │       ├─► Update status to 'pending'
    │       └─► Enqueue to RQ
    │
    ▼
RQ Worker picks up task
    │
    ├─► process_campaign_task()
    │       │
    │       ├─► Update status to 'processing'
    │       │
    │       └─► For each pending CampaignLead:
    │               │
    │               ├─► process_campaign_lead_with_graph()
    │               │       │
    │               │       ├─► Initialize LangGraph state
    │               │       ├─► Run workflow
    │               │       └─► Save results
    │               │
    │               └─► Update CampaignLead status
    │
    └─► Update Campaign status to 'completed'
```

### LangGraph Workflow

```
┌─────────────────────────────────────────────────┐
│              LangGraph State Machine            │
├─────────────────────────────────────────────────┤
│                                                 │
│  START                                          │
│    │                                            │
│    ▼                                            │
│  ┌──────────────┐                              │
│  │  Validate    │                              │
│  │  Lead Node   │                              │
│  └──────┬───────┘                              │
│         │                                       │
│    ┌────┴─────┐                                │
│    │          │                                 │
│    ▼          ▼                                 │
│  Failed    Passed                               │
│    │          │                                 │
│    │          ▼                                 │
│    │    ┌──────────────┐                       │
│    │    │  SMS Agent   │                       │
│    │    │  Node        │                       │
│    │    └──────┬───────┘                       │
│    │           │                                │
│    │           ├─► Generate SMS (OpenAI)       │
│    │           ├─► Calculate cost              │
│    │           └─► Send SMS (mock)             │
│    │           │                                │
│    └───────────┤                                │
│                ▼                                 │
│          ┌──────────────┐                       │
│          │  Finalize    │                       │
│          │  Node        │                       │
│          └──────┬───────┘                       │
│                 │                                │
│                 ├─► Determine status            │
│                 ├─► Save logs                   │
│                 └─► Update stats                │
│                 │                                │
│                 ▼                                │
│               END                                │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Database Schema

### Tables

#### leads
```sql
CREATE TABLE leads (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    company VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

#### campaigns
```sql
CREATE TABLE campaigns (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    agent_type VARCHAR(50) NOT NULL,  -- 'sms', 'voice', 'both'
    status VARCHAR(50) NOT NULL,       -- 'draft', 'pending', 'processing', 'completed', 'failed'
    sms_system_prompt TEXT,
    sms_temperature INTEGER DEFAULT 70,
    stats JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

#### campaign_leads
```sql
CREATE TABLE campaign_leads (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    lead_id INTEGER REFERENCES leads(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending',
    sms_sent BOOLEAN DEFAULT FALSE,
    sms_message TEXT,
    sms_response TEXT,
    voice_call_made BOOLEAN DEFAULT FALSE,
    trace_id VARCHAR(255),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    processed_at TIMESTAMP
);
```

#### processing_logs
```sql
CREATE TABLE processing_logs (
    id SERIAL PRIMARY KEY,
    campaign_lead_id INTEGER REFERENCES campaign_leads(id) ON DELETE CASCADE,
    level VARCHAR(20) NOT NULL,
    node_name VARCHAR(100),
    message TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## API Endpoints

### Campaigns

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/campaigns` | List all campaigns |
| GET | `/api/campaigns/{id}` | Get campaign details |
| POST | `/api/campaigns` | Create new campaign |
| PUT | `/api/campaigns/{id}` | Update campaign |
| DELETE | `/api/campaigns/{id}` | Delete campaign |
| POST | `/api/campaigns/{id}/start` | Start campaign processing |
| GET | `/api/campaigns/{id}/logs` | Get processing logs |

### Leads

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/leads` | List all leads |
| GET | `/api/leads/{id}` | Get lead details |
| POST | `/api/leads` | Create new lead |
| PUT | `/api/leads/{id}` | Update lead |
| DELETE | `/api/leads/{id}` | Delete lead |

### Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/stats` | Get dashboard statistics |
| GET | `/api/dashboard/recent-campaigns` | Get recent campaigns |

## State Management

### LangGraph State

```python
class CampaignLeadState(TypedDict):
    # Identifiers
    campaign_lead_id: str
    campaign_id: str
    lead_id: str
    
    # Lead data
    lead_data: Dict[str, Any]
    
    # Configuration
    agent_type: str
    sms_system_prompt: str
    sms_temperature: float
    
    # Results
    validation_passed: bool
    validation_errors: List[str]
    sms_sent: bool
    sms_message: str
    sms_error: str
    sms_cost: float
    
    # Metadata
    processing_logs: List[Dict]
    trace_id: str
    status: str
    error_message: str
```

## Error Handling

### Backend
- All API endpoints return appropriate HTTP status codes
- Validation errors return 422 with detailed messages
- Database errors are caught and logged
- LangGraph node failures are captured in processing logs

### Frontend
- React Query handles API errors gracefully
- Loading states for all async operations
- Error messages displayed to users
- Automatic retry for failed requests

## Performance Considerations

### Backend
- Database connection pooling (10 connections)
- Async FastAPI for concurrent requests
- Background task processing with RQ
- Efficient database queries with SQLAlchemy

### Frontend
- React Query caching (5-second refetch interval)
- Code splitting with Vite
- Optimized re-renders with React 18
- TailwindCSS for minimal CSS bundle

## Security

### Current (POC)
- CORS enabled for localhost
- No authentication (development only)
- Environment variables for secrets
- SQL injection prevention (SQLAlchemy)

### Production TODO
- [ ] JWT authentication
- [ ] Rate limiting
- [ ] Input sanitization
- [ ] HTTPS only
- [ ] API key rotation
- [ ] Role-based access control

## Scalability

### Current Capacity
- Sequential lead processing
- Single RQ worker
- SQLite/PostgreSQL
- ~100 leads per campaign

### Future Improvements
- [ ] Parallel lead processing
- [ ] Multiple RQ workers
- [ ] Redis caching
- [ ] Database read replicas
- [ ] Horizontal scaling with Kubernetes

## Monitoring

### Available
- FastAPI automatic API docs
- RQ worker console logs
- Database query logging
- LangSmith tracing (optional)

### Future
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] Sentry error tracking
- [ ] CloudWatch/DataDog integration

## Testing Strategy

### Backend
- Unit tests for services
- Integration tests for API endpoints
- LangGraph workflow tests
- Database migration tests

### Frontend
- Component unit tests
- Integration tests with React Testing Library
- E2E tests with Playwright (future)

## Deployment

### Development
```bash
# Backend
uvicorn app.main:app --reload

# Worker
python worker.py

# Frontend
npm run dev
```

### Production (Future)
```bash
# Backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Worker
rq worker campaigns --burst

# Frontend
npm run build
# Serve with nginx or CDN
```

## Comparison with Django POC

| Aspect | Django POC | FastAPI POC |
|--------|-----------|-------------|
| **Framework** | Django 5.x | FastAPI 0.115 |
| **Admin** | Django Admin | React SPA |
| **API Docs** | DRF Swagger | Auto-generated OpenAPI |
| **Async** | Limited (ASGI) | Native async/await |
| **Type Safety** | Partial | Full (Pydantic) |
| **Performance** | ~1000 req/s | ~5000 req/s |
| **Learning Curve** | Moderate | Low |
| **Ecosystem** | Mature | Growing |

## Key Design Decisions

### Why FastAPI?
- Modern async support
- Automatic API documentation
- Type safety with Pydantic
- High performance
- Easy to learn

### Why LangGraph?
- Declarative workflow definition
- Built-in state management
- Easy to visualize and debug
- Conditional routing support
- LangSmith integration

### Why React?
- Component-based architecture
- Large ecosystem
- TypeScript support
- Modern tooling (Vite)
- Easy to extend

### Why RQ over Celery?
- Simpler setup for POC
- Fewer dependencies
- Good enough for most use cases
- Easy to migrate to Celery later

## Next Steps

1. **Phase 2**: Add voice campaign support
2. **Phase 3**: Implement agent configuration UI
3. **Phase 4**: Add knowledge base (RAG)
4. **Phase 5**: Multi-agent orchestration
5. **Phase 6**: Production deployment

---

**Questions?** Review the code comments or check the Django POC for additional context.

