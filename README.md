# FastAPI LangGraph POC - SMS Campaign Platform

A proof-of-concept SMS campaign platform built with **FastAPI**, **LangChain**, **LangGraph**, and **React**.

## 🎯 Purpose

Demonstrate how LangChain/LangGraph can orchestrate SMS campaigns with:
- State machine workflow management
- AI-powered message generation
- Background task processing
- Real-time campaign monitoring

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         React Frontend                           │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐ │
│  │ Dashboard  │  │ Campaigns  │  │   Leads    │  │  Results  │ │
│  └────────────┘  └────────────┘  └────────────┘  └───────────┘ │
└────────────────────────────────┬────────────────────────────────┘
                                 │ REST API
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Backend                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐ │
│  │ Campaigns  │  │   Leads    │  │  Results   │  │ Dashboard │ │
│  └────────────┘  └────────────┘  └────────────┘  └───────────┘ │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   Celery + Redis        │
                    └────────────┬────────────┘
                                 │
                                 ▼
        ┌────────────────────────────────────────────────┐
        │         LangGraph Orchestrator                 │
        │  ┌──────────────────────────────────────────┐  │
        │  │   Campaign Lead State Machine            │  │
        │  │                                          │  │
        │  │   ┌──────────┐                          │  │
        │  │   │ Validate │                          │  │
        │  │   └─────┬────┘                          │  │
        │  │         │                                │  │
        │  │         ▼                                │  │
        │  │   ┌──────────┐                          │  │
        │  │   │   SMS    │                          │  │
        │  │   │  Agent   │                          │  │
        │  │   └─────┬────┘                          │  │
        │  │         │                                │  │
        │  │         ▼                                │  │
        │  │   ┌──────────┐                          │  │
        │  │   │Finalize  │                          │  │
        │  │   └──────────┘                          │  │
        │  └──────────────────────────────────────────┘  │
        └────────────────┬───────────────────────────────┘
                         │
                         ▼
            ┌─────────────────┐
            │  OpenAI Service │
            │   (LangChain)   │
            └─────────────────┘
```

## 📦 Tech Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **SQLAlchemy 2.0** - Async ORM
- **Alembic** - Database migrations
- **Celery** - Background task processing
- **Redis** - Task queue broker
- **LangChain** - LLM framework
- **LangGraph** - Workflow orchestration
- **PostgreSQL** - Database

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TanStack Query** - API state management
- **Tailwind CSS** - Styling
- **Shadcn/ui** - Component library

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- OpenAI API key

### 1. Clone and Setup

```bash
cd fastapi-langgraph-poc
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

### 2. Start Services (Docker)

```bash
docker-compose up -d
```

This starts:
- FastAPI backend (http://localhost:8000)
- React frontend (http://localhost:5173)
- PostgreSQL database
- Redis
- Celery worker

### 3. Run Migrations

```bash
docker-compose exec backend alembic upgrade head
```

### 4. Create Sample Data

```bash
docker-compose exec backend python scripts/create_sample_leads.py
```

### 5. Test Campaign

```bash
docker-compose exec backend python scripts/test_campaign.py sms 10
```

## 📁 Project Structure

```
fastapi-langgraph-poc/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── database.py          # DB connection
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── api/
│   │   │   ├── campaigns.py     # Campaign endpoints
│   │   │   ├── leads.py         # Lead endpoints
│   │   │   └── dashboard.py     # Dashboard endpoints
│   │   ├── orchestrator/        # LangGraph logic
│   │   │   ├── state.py         # State definitions
│   │   │   ├── nodes.py         # Graph nodes
│   │   │   └── graph.py         # Workflow compilation
│   │   ├── services/
│   │   │   └── openai_service.py # OpenAI integration
│   │   └── tasks/
│   │       └── campaign_tasks.py # Celery tasks
│   ├── alembic/                 # Database migrations
│   ├── scripts/                 # Utility scripts
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── pages/
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── CampaignsPage.tsx
│   │   │   ├── CampaignDetailPage.tsx
│   │   │   └── LeadsPage.tsx
│   │   ├── components/
│   │   │   ├── CampaignCard.tsx
│   │   │   ├── CampaignForm.tsx
│   │   │   ├── LeadTable.tsx
│   │   │   └── StatsCard.tsx
│   │   └── api/
│   │       └── client.ts
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔑 Key Features

### 1. LangGraph State Machine
Declarative workflow definition for campaign processing:
- Validate lead data
- Generate personalized SMS with OpenAI
- Track results and costs
- Handle errors gracefully

### 2. Async FastAPI
- High-performance async endpoints
- Auto-generated OpenAPI docs at `/docs`
- Type-safe with Pydantic
- Dependency injection

### 3. React Dashboard
- Real-time campaign monitoring
- Create and manage campaigns
- View processing logs
- Track costs and success rates

### 4. Background Processing
- Celery for reliable task execution
- Redis for fast message brokering
- Parallel lead processing
- Automatic retries

## 📊 API Endpoints

### Campaigns
- `POST /api/campaigns` - Create campaign
- `GET /api/campaigns` - List campaigns
- `GET /api/campaigns/{id}` - Get campaign details
- `POST /api/campaigns/{id}/start` - Start processing
- `GET /api/campaigns/{id}/results` - View results
- `GET /api/campaigns/{id}/logs` - View logs

### Leads
- `POST /api/leads` - Create lead
- `GET /api/leads` - List leads
- `POST /api/leads/bulk` - Bulk create

### Dashboard
- `GET /api/dashboard/stats` - Statistics

### Documentation
- `GET /docs` - Interactive API docs (Swagger)
- `GET /redoc` - Alternative API docs

## 🧪 Testing

### Test SMS Campaign
```bash
python scripts/test_campaign.py sms 10
```

### Monitor Celery Worker
```bash
docker-compose logs -f celery
```

### View API Logs
```bash
docker-compose logs -f backend
```

## 💰 Cost Tracking

All OpenAI API costs are tracked automatically:
- Per-lead cost
- Per-campaign total
- Token usage
- Model information

View in dashboard or via API.

## 🔮 Future Enhancements

- [ ] Voice campaign support (ElevenLabs)
- [ ] Real-time WebSocket updates
- [ ] A/B testing for prompts
- [ ] Multi-agent conversations
- [ ] RAG knowledge base integration
- [ ] Webhook support
- [ ] Email campaigns

## 📚 Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [API Reference](http://localhost:8000/docs)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 🤝 Comparison with Django POC

| Feature | Django POC | FastAPI POC |
|---------|------------|-------------|
| Framework | Django REST | FastAPI |
| ORM | Django ORM | SQLAlchemy |
| Task Queue | RQ | Celery |
| Frontend | Admin Panel | React SPA |
| Async | Limited | Full async |
| API Docs | Manual | Auto-generated |
| Performance | Good | Excellent |

## 📝 License

MIT

## 🙋 Support

For questions or issues, check the documentation or review the inline code comments.
