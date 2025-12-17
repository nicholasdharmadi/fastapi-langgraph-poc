"""FastAPI application entry point."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import campaigns, leads, dashboard, settings, workflows, conversations, traces, agents, campaign_leads, prompt_builder
from app.database import Base, engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="FastAPI LangGraph POC",
    description="SMS Campaign Management with LangGraph",
    version="1.0.0",
    redirect_slashes=False  # Prevent 307 redirects that leak Docker hostnames
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(campaigns.router, prefix="/api")
app.include_router(leads.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(workflows.router, prefix="/api")
app.include_router(conversations.router, prefix="/api")
app.include_router(traces.router, prefix="/api")
app.include_router(agents.router, prefix="/api")
app.include_router(campaign_leads.router, prefix="/api")
app.include_router(prompt_builder.router, prefix="/api")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "FastAPI LangGraph POC",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

