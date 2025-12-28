# News Processing System - Backend

Production-ready real-time news processing pipeline with sentiment analysis and LLM summarization.

## Directory Structure

```
backend/
├── app/                         # FastAPI application
│   ├── routes/                  # API endpoints
│   ├── models/                  # Pydantic models
│   ├── services/                # Business logic
│   ├── database.py              # MongoDB connection
│   └── config.py                # App configuration
│
├── services/                    # Microservices
│   ├── news-scraper/            # Layer 1: RSS metadata scraper
│   ├── enrichment-pipeline/     # Layer 2: Content & sentiment
│   └── llm-worker/              # Layer 3: AI summarization
│
├── data-collection/             # Legacy scraper (for reference)
│
├── main.py                      # FastAPI entry point
├── requirements.txt             # Python dependencies
├── Dockerfile                   # FastAPI container
├── .env.example                 # Environment template
└── .env.remote-example          # Remote MongoDB template
```

## Quick Start

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your MONGODB_URI and GEMINI_API_KEY

# 2. Start with Docker Compose (from project root)
docker-compose up -d

# 3. Initialize search config
docker exec -it news-scraper python /app/setup_search_config.py

# 4. Check health
curl http://localhost:8000/health
```

## Services

### 1. News Scraper
- Scrapes Google News RSS feeds
- Multi-layer deduplication (Bloom Filter + Redis + MongoDB)
- Stores raw articles to MongoDB

### 2. Enrichment Pipeline
- Fetches full article content
- Runs FinBERT sentiment analysis
- Feature extraction (liquidity impact, critical events)
- Story clustering

### 3. LLM Worker
- Summarizes articles using Gemini AI
- Relevance filtering
- Financial impact assessment

### 4. FastAPI Backend
- REST API for querying articles
- Search configuration management
- Statistics and monitoring

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/news/summarized` | Get summarized articles with filters |
| `GET /api/news/enriched` | Get enriched articles |
| `GET /api/news/clusters` | Get story clusters |
| `GET /api/news/companies` | List configured companies |
| `PUT /api/news/config` | Update search config |
| `GET /api/news/stats` | Pipeline statistics |
| `GET /health` | Health check |

## MongoDB Collections

| Collection | Description |
|------------|-------------|
| `raw_articles` | Scraped metadata from news-scraper |
| `enriched_articles` | Articles with sentiment from enrichment-pipeline |
| `summarize` | LLM summaries from llm-worker |
| `story_clusters` | Grouped related articles |
| `url_registry` | Deduplication registry |

## Environment Variables

```bash
# Required
MONGODB_URI=mongodb+srv://...
MONGODB_DB=news_db
MONGODB_CONFIG_DB=config_db
GEMINI_API_KEY=your_key

# Optional
REDIS_HOST=redis
REDIS_PORT=6379
SCRAPE_INTERVAL=300
MAX_CONCURRENT_STRATEGIES=10
RATE_LIMIT_RPM=2000
```

## Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Specific service
docker-compose logs -f news-scraper

# Rebuild after changes
docker-compose build news-scraper
docker-compose up -d news-scraper

# Stop all
docker-compose down
```

## Architecture

```
News Sources → Scraper → MongoDB → Enrichment → MongoDB → LLM Worker → MongoDB
               (Dedup)   (raw)    (Content+     (enriched)  (Summarize)  (summarize)
                                   Sentiment)
                                         ↑
                         FastAPI REST API┘
```

**Key Features:**
- 3-layer deduplication (Bloom Filter + Redis + MongoDB)
- FinBERT sentiment analysis
- Google Gemini API integration
- Horizontally scalable workers
- MongoDB-native (no Kafka required)
- Complete Docker orchestration
