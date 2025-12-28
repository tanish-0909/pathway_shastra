#!/bin/bash

# =========================================
# Complete Platform Setup Script
# Includes: Infrastructure + News Pipeline
# =========================================

set -e

echo "========================================="
echo "Financial Intelligence Platform - Setup"
echo "========================================="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! docker compose version &> /dev/null 2>&1; then
    echo "Docker Compose is not installed."
    exit 1
fi

echo "Docker and Docker Compose found"
echo ""

# Navigate to project root
cd "$(dirname "$0")" || exit 1

# Check/Create .env file in backend
if [ ! -f "backend/.env" ]; then
    echo "backend/.env not found"
    echo "Creating from template..."
    
    echo ""
    echo "Please enter your MongoDB URI (e.g., mongodb+srv://user:pass@cluster.mongodb.net/):"
    read -r MONGODB_URI
    
    if [ -z "$MONGODB_URI" ]; then
        echo "MongoDB URI is required!"
        exit 1
    fi
    
    echo ""
    echo "Please enter your Gemini API key (get from https://ai.google.dev/):"
    read -r GEMINI_KEY
    
    if [ -z "$GEMINI_KEY" ]; then
        echo "Gemini API key is required!"
        exit 1
    fi
    
    cat > backend/.env << EOF
# MongoDB Configuration
MONGODB_URI=$MONGODB_URI
MONGODB_DB=news_db
MONGODB_CONFIG_DB=config_db

# Redis Configuration (Docker internal)
REDIS_HOST=redis
REDIS_PORT=6379

# Scraper Configuration
SCRAPE_INTERVAL=300
TEST_COMPANY=all
MAX_CONCURRENT_STRATEGIES=10

# Enrichment Configuration
MAX_CONCURRENT_FETCHES=20
POLL_INTERVAL=5

# LLM Worker Configuration
GEMINI_API_KEY=$GEMINI_KEY
WORKER_ID=worker-1
RATE_LIMIT_RPM=2000
MAX_CONCURRENT_REQUESTS=50

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
EOF
    
    echo "Created backend/.env"
else
    echo "backend/.env exists"
    
    # Check if required keys are set
    if ! grep -q "MONGODB_URI=" backend/.env || grep -q "MONGODB_URI=$" backend/.env; then
        echo "MONGODB_URI not set in .env"
        echo "Please enter your MongoDB URI:"
        read -r MONGODB_URI
        
        if [ -n "$MONGODB_URI" ]; then
            echo "MONGODB_URI=$MONGODB_URI" >> backend/.env
            echo "Added MONGODB_URI to .env"
        fi
    fi
    
    if ! grep -q "GEMINI_API_KEY=" backend/.env || grep -q "GEMINI_API_KEY=$" backend/.env; then
        echo "GEMINI_API_KEY not set in .env"
        echo "Please enter your Gemini API key:"
        read -r GEMINI_KEY
        
        if [ -n "$GEMINI_KEY" ]; then
            echo "GEMINI_API_KEY=$GEMINI_KEY" >> backend/.env
            echo "Added GEMINI_API_KEY to .env"
        fi
    fi
fi

echo ""
echo "========================================="
echo "Building & Starting Services"
echo "========================================="
echo ""

# Build services
echo "Building Docker images..."
docker compose build

# Start all services
echo ""
echo "Starting all services..."
echo "  - Infrastructure: Redis"
echo "  - News Pipeline: scraper, enrichment-pipeline, llm-worker"
echo "  - API: FastAPI on port 8000"
echo ""

docker compose up -d

echo ""
echo "Waiting for services to be healthy (20s)..."
sleep 20

# Check service status
echo ""
echo "Service Status:"
docker compose ps

echo ""
echo "========================================="
echo "Initializing Search Configuration"
echo "========================================="
echo ""

# Wait for MongoDB
echo "Waiting for MongoDB connection..."
sleep 5

# Initialize search config (non-interactive)
echo "Setting up search configuration..."
if docker exec news-scraper python setup_search_config.py 2>/dev/null; then
    echo "Search configuration initialized"
else
    echo "Failed to initialize search config. You can run it manually:"
    echo "   docker exec news-scraper python setup_search_config.py"
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Services Running:"
echo "  - Redis:             localhost:6379"
echo "  - FastAPI:           http://localhost:8000"
echo "  - API Docs:          http://localhost:8000/docs"
echo ""
echo "Quick Tests:"
echo "  # Check API health"
echo "  curl http://localhost:8000/health"
echo ""
echo "  # Get news stats"
echo "  curl http://localhost:8000/api/news/stats"
echo ""
echo "  # Check Redis"
echo "  docker exec redis redis-cli ping"
echo ""
echo "Useful Commands:"
echo "  View all logs:       docker compose logs -f"
echo "  View scraper logs:   docker compose logs -f news-scraper"
echo "  View enrichment:     docker compose logs -f enrichment-pipeline"
echo "  View LLM worker:     docker compose logs -f llm-worker"
echo "  Stop services:       docker compose down"
echo "  Restart services:    docker compose restart"
echo ""
echo "Note: It may take 5-10 minutes for articles to start appearing."
echo "      Monitor progress: docker compose logs -f news-scraper"
echo ""
