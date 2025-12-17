#!/bin/bash

# FastAPI LangGraph POC - Quick Start Script
# This script sets up the project for development

set -e

echo "🚀 FastAPI LangGraph POC - Quick Start"
echo "======================================="
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function for Docker setup
setup_docker() {
    echo "🐳 Setting up with Docker..."
    
    if ! command_exists docker; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi

    if [ ! -f ".env" ]; then
        echo "Creating .env file for Docker..."
        echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
        echo ""
        echo "⚠️  IMPORTANT: Edit the .env file in the root directory and add your OPENAI_API_KEY"
        echo "   (Press Enter to continue after editing, or Ctrl+C to exit)"
        read -r
    fi

    echo "Building and starting services..."
    docker-compose up --build
}

# Function for Local setup
setup_local() {
    echo "💻 Setting up for Local Development..."

    # Check prerequisites
    echo "📋 Checking prerequisites..."

    if ! command_exists python3; then
        echo "❌ Python 3 is not installed"
        exit 1
    fi

    if ! command_exists node; then
        echo "❌ Node.js is not installed"
        exit 1
    fi

    if ! command_exists psql; then
        echo "⚠️  PostgreSQL client not found. Make sure PostgreSQL is installed and running."
    fi

    if ! command_exists redis-cli; then
        echo "⚠️  Redis client not found. Make sure Redis is installed and running."
    fi

    echo "✅ Prerequisites check complete"
    echo ""

    # Backend setup
    echo "🐍 Setting up backend..."
    cd backend

    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi

    echo "Activating virtual environment..."
    source venv/bin/activate

    echo "Installing Python dependencies..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt

    if [ ! -f ".env" ]; then
        echo "Creating .env file..."
        cp env.example .env
        echo ""
        echo "⚠️  IMPORTANT: Edit backend/.env and add your:"
        echo "   - DATABASE_URL"
        echo "   - REDIS_URL"
        echo "   - OPENAI_API_KEY"
        echo ""
        read -p "Press Enter after you've updated the .env file..."
    fi

    echo "Creating database tables..."
    python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)" 2>/dev/null || echo "⚠️  Database tables may already exist"

    echo "Seeding sample data..."
    python seed_data.py

    echo "✅ Backend setup complete"
    echo ""

    cd ..

    # Frontend setup
    echo "⚛️  Setting up frontend..."
    cd frontend

    if [ ! -d "node_modules" ]; then
        echo "Installing Node.js dependencies..."
        npm install
    fi

    echo "✅ Frontend setup complete"
    echo ""

    cd ..

    # Final instructions
    echo "🎉 Setup Complete!"
    echo "=================="
    echo ""
    echo "To start the application locally:"
    echo ""
    echo "1. Start PostgreSQL and Redis (if not already running)"
    echo ""
    echo "2. Terminal 1 - Backend API:"
    echo "   cd backend"
    echo "   source venv/bin/activate"
    echo "   uvicorn app.main:app --reload"
    echo ""
    echo "3. Terminal 2 - RQ Worker:"
    echo "   cd backend"
    echo "   source venv/bin/activate"
    echo "   python worker.py"
    echo ""
    echo "4. Terminal 3 - Frontend:"
    echo "   cd frontend"
    echo "   npm run dev"
    echo ""
    echo "Then visit:"
    echo "  - Frontend: http://localhost:3000"
    echo "  - API: http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo ""
    echo "Happy coding! 🚀"
}

# Main Menu
echo "Choose setup mode:"
echo "1) Docker (Recommended - Runs everything together)"
echo "2) Local (For development on host machine)"
echo ""
read -p "Enter choice [1/2]: " choice

case $choice in
    1)
        setup_docker
        ;;
    2)
        setup_local
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac
