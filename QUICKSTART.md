# Quick Start Guide

Get up and running with the FastAPI LangGraph POC in 5 minutes!

## 🚀 Option 1: Docker (Recommended)

### Prerequisites
- Docker & Docker Compose installed
- OpenAI API key

### Steps

1. **Setup Environment**
```bash
cd fastapi-langgraph-poc
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```bash
OPENAI_API_KEY=sk-your-key-here
```

2. **Start Everything**
```bash
chmod +x quickstart.sh
./quickstart.sh
```

Or manually:
```bash
docker-compose up -d
docker-compose exec backend python scripts/create_sample_leads.py
```

3. **Access the Application**
- 🌐 Frontend: http://localhost:5173
- 🔌 API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs

4. **Run a Test Campaign**
```bash
docker-compose exec backend python scripts/test_campaign.py sms 10
```

## 🛠️ Option 2: Manual Setup

### Backend

1. **Install Dependencies**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp env.example .env
# Edit .env with your settings
```

3. **Setup Database**
```bash
# Start PostgreSQL (or use SQLite by changing DATABASE_URL)
# Create database: langgraph_poc

# Create tables
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Add sample data
python scripts/create_sample_leads.py
```

4. **Start Services**

Terminal 1 - API:
```bash
uvicorn app.main:app --reload
```

Terminal 2 - Worker:
```bash
python worker.py
```

Terminal 3 - Redis:
```bash
redis-server
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173

## 🧪 Testing

### Create a Campaign

**Via UI:**
1. Go to http://localhost:5173/campaigns
2. Click "New Campaign"
3. Fill in details
4. Click "Start Campaign"

**Via API:**
```bash
curl -X POST http://localhost:8000/api/campaigns/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Campaign",
    "agent_type": "sms",
    "sms_system_prompt": "You are a friendly sales assistant.",
    "sms_temperature": 70,
    "lead_count": 5
  }'
```

### Run Test Script

```bash
# Docker
docker-compose exec backend python scripts/test_campaign.py sms 10

# Local
cd backend
python scripts/test_campaign.py sms 10
```

## 📊 Monitoring

### View Logs

**Docker:**
```bash
docker-compose logs -f backend
docker-compose logs -f worker
docker-compose logs -f frontend
```

**Local:**
Check terminal outputs

### Check Status

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Campaign Status:**
```bash
curl http://localhost:8000/api/campaigns/1
```

**Processing Logs:**
```bash
curl http://localhost:8000/api/campaigns/1/logs
```

## 🔧 Common Issues

### Backend won't start
- ✅ Check `.env` file exists and has OPENAI_API_KEY
- ✅ Verify PostgreSQL/Redis are running
- ✅ Check port 8000 is not in use

### Worker not processing
- ✅ Check Redis is running: `redis-cli ping`
- ✅ Verify worker is running: `docker-compose ps worker`
- ✅ Check worker logs: `docker-compose logs worker`

### Frontend can't connect
- ✅ Verify backend is running on port 8000
- ✅ Check CORS settings in `backend/app/main.py`
- ✅ Clear browser cache

### Database errors
- ✅ Check DATABASE_URL in `.env`
- ✅ Verify database exists
- ✅ Run migrations if needed

## 🎯 Next Steps

1. **Explore the UI**
   - Create campaigns
   - View results
   - Check logs

2. **Try the API**
   - Visit http://localhost:8000/docs
   - Test endpoints interactively

3. **Customize**
   - Edit system prompts
   - Adjust temperature
   - Add more leads

4. **Extend**
   - Add voice campaigns
   - Implement RAG
   - Add webhooks

## 📚 Documentation

- [README.md](README.md) - Project overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment
- [API Docs](http://localhost:8000/docs) - Interactive API documentation

## 🆘 Getting Help

1. Check the logs for error messages
2. Review the documentation
3. Check the Django POC for reference
4. Review inline code comments

## 🛑 Stopping Services

**Docker:**
```bash
docker-compose down
```

**Manual:**
- Press Ctrl+C in each terminal
- Stop PostgreSQL and Redis if you started them

## 🗑️ Clean Up

**Remove all data:**
```bash
docker-compose down -v
```

**Reset database:**
```bash
docker-compose exec backend python -c "from app.database import Base, engine; Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)"
docker-compose exec backend python scripts/create_sample_leads.py
```

---

**Happy coding!** 🚀



