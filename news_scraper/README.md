# Financial Intelligence Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Real-time financial news intelligence pipeline with multi-layer deduplication, sentiment analysis, and LLM-powered summarization.

## Features

- **Automated News Collection**: Scrapes financial news from Google News RSS
- **Multi-layer Deduplication**: URL, content, and fuzzy title matching
- **Sentiment Analysis**: FinBERT-based sentiment classification
- **LLM Summarization**: Gemini-powered article summarization and impact assessment
- **Story Clustering**: Groups related articles from multiple sources
- **REST API**: Query articles with filters (company, sentiment, date, etc.)
- **MongoDB Storage**: Direct writes to MongoDB Atlas (no Kafka required)

## Architecture

```
News Scraper → MongoDB → Enrichment Pipeline → MongoDB → LLM Worker → MongoDB
     ↓            ↑              ↓                 ↑          ↓          ↑
  raw_articles    │    enriched_articles           │    summarize        │
                  └────────────────────────────────┴─────────────────────┘
                                    FastAPI (REST API)
```

**Services:**
- **News Scraper**: Fetches article metadata (title, URL, source) and stores to MongoDB
- **Enrichment Pipeline**: Polls MongoDB for new articles, fetches content, runs sentiment analysis
- **LLM Worker**: Summarizes enriched articles using Gemini AI
- **FastAPI**: REST API for querying processed articles

**Infrastructure:**
- **Redis**: Caching and deduplication (Bloom filters)
- **MongoDB Atlas**: Persistent storage (managed cloud database)

## Quick Start

### Prerequisites

- Docker & Docker Compose
- MongoDB Atlas account ([Create free cluster](https://www.mongodb.com/cloud/atlas/register))
- Gemini API key ([Get one here](https://ai.google.dev/))
- 8GB+ RAM recommended

### Setup

```bash
# Clone repository
git clone <your-repo-url>
cd upgraded-octo-spork

# Configure environment
cp backend/.env.example backend/.env

# Edit backend/.env with your credentials:
# - MONGODB_URI: Your MongoDB Atlas connection string
# - GEMINI_API_KEY: Your Gemini API key

# Start services
docker-compose up -d

# Initialize search config (first time only)
docker exec -it news-scraper python /app/setup_search_config.py

# Verify - API should respond
curl http://localhost:8000/health
curl http://localhost:8000/api/news/stats
```

**What `docker-compose up -d` starts:**
- **Infrastructure**: Redis (for caching/dedup)
- **News Pipeline**: news-scraper → enrichment-pipeline → llm-worker
- **FastAPI Backend**: REST API server on port 8000
- **All networking**: Internal docker network with proper service discovery

**Access Points:**
- **FastAPI**: http://localhost:8000/docs (Interactive API docs)
- **News API**: http://localhost:8000/api/news/* (Articles, companies, stats)
- **Redis**: localhost:6379

## API Examples

### Get Summarized Articles

```bash
# All articles
GET /api/news/summarized?limit=10

# Filter by company
GET /api/news/summarized?company=tcs&limit=5

# Filter by sentiment
GET /api/news/summarized?company=itc&sentiment=negative

# Date range
GET /api/news/summarized?start_date=2024-12-01&end_date=2024-12-02
```

### Get Companies

```bash
GET /api/news/companies
```

### Update Search Config

```bash
PUT /api/news/config
{
  "company_code": "tcs",
  "theme": "regulatory",
  "query": "(\"TCS\" OR \"Tata Consultancy\") AND (regulation OR compliance) -job"
}
```

### Get Statistics

```bash
GET /api/news/stats
```

See full API documentation at http://localhost:8000/docs

## Project Structure

```
.
├── backend/
│   ├── app/                       # FastAPI application
│   │   ├── routes/
│   │   │   ├── news.py            # News API endpoints
│   │   │   └── ...
│   │   ├── models/
│   │   │   └── news.py            # Pydantic models
│   │   ├── database.py            # MongoDB connection
│   │   └── config.py              # App configuration
│   │
│   ├── services/                  # Microservices
│   │   ├── news-scraper/          # Layer 1: RSS scraping
│   │   ├── enrichment-pipeline/   # Layer 2: Content & sentiment
│   │   └── llm-worker/            # Layer 3: LLM summarization
│   │
│   ├── main.py                    # FastAPI entry point
│   └── Dockerfile
│
├── docker-compose.yml             # All services
└── README.md
```

## Configuration

### Environment Variables

```bash
# Required
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DB=news_db
MONGODB_CONFIG_DB=config_db
GEMINI_API_KEY=your_gemini_api_key

# Optional (defaults shown)
REDIS_HOST=redis
REDIS_PORT=6379
SCRAPE_INTERVAL=300  # 5 minutes
MAX_CONCURRENT_STRATEGIES=10
RATE_LIMIT_RPM=2000  # Gemini rate limit
```

### Adding Companies

```bash
# Via API
POST /api/news/config/company
{
  "company_code": "reliance",
  "aliases": ["Reliance", "Reliance Industries", "RIL"]
}

# Via script
docker exec -it news-scraper python /app/setup_search_config.py
```

## Monitoring

### Service Health

```bash
# API health
curl http://localhost:8000/health

# Service status
docker-compose ps

# Logs
docker-compose logs -f

# Individual service logs
docker-compose logs -f news-scraper
docker-compose logs -f enrichment-pipeline
docker-compose logs -f llm-worker
```

### MongoDB Queries

```bash
# Connect to Atlas with mongosh
mongosh "$MONGODB_URI"

# Or use the API
curl http://localhost:8000/api/news/stats
```

## Development

```bash
# Start only infrastructure
docker-compose up -d redis

# Run FastAPI locally
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Run specific service
docker-compose up -d news-scraper

# Rebuild after code changes
docker-compose build news-scraper
docker-compose up -d news-scraper
```

## MongoDB Collections

The system uses the following MongoDB collections:

| Collection | Description |
|------------|-------------|
| `raw_articles` | Scraped article metadata (from news-scraper) |
| `enriched_articles` | Articles with sentiment & content (from enrichment-pipeline) |
| `summarize` | LLM-summarized articles (from llm-worker) |
| `story_clusters` | Grouped related articles |
| `url_registry` | URL deduplication registry |

## Troubleshooting

### No articles appearing?

```bash
# Check scraper logs
docker-compose logs -f news-scraper

# Verify config loaded via API
curl http://localhost:8000/api/news/companies
```

### Pipeline not processing?

```bash
# Check for unprocessed articles
docker exec -it api python -c "
from pymongo import MongoClient
import os
client = MongoClient(os.environ.get('MONGODB_URI'))
db = client['news_db']
print('Raw articles:', db.raw_articles.count_documents({'processed': False}))
print('Unsummarized:', db.enriched_articles.count_documents({'summarized': {'$ne': True}}))
"
```

### Can't connect to MongoDB Atlas?

```bash
# Test connection string
mongosh "$MONGODB_URI" --eval "db.adminCommand('ping')"

# Check API logs
docker logs api -f
```

## Integration with News Agent

To integrate this news scraper with your news agent:

1. **Query the API** - Your agent can call the REST API to get summarized news:
   ```python
   import requests
   
   # Get latest news for a company
   response = requests.get(
       "http://localhost:8000/api/news/summarized",
       params={"company": "tcs", "limit": 10}
   )
   articles = response.json()
   ```

2. **Direct MongoDB Access** - Or query MongoDB directly:
   ```python
   from pymongo import MongoClient
   
   client = MongoClient(os.environ.get('MONGODB_URI'))
   db = client['news_db']
   
   # Get summarized articles
   articles = list(db.summarize.find({
       "company": "tcs",
       "is_relevant": True
   }).sort("published_at", -1).limit(10))
   ```

3. **Webhook/Polling** - Set up a polling mechanism to check for new articles:
   ```python
   # Query for articles since last check
   from datetime import datetime, timedelta
   
   since = (datetime.utcnow() - timedelta(hours=1)).isoformat()
   new_articles = list(db.summarize.find({
       "summarized_at": {"$gte": since}
   }))
   ```

## License

MIT License - see LICENSE for details

## Acknowledgments

- **FinBERT**: Financial sentiment analysis
- **Gemini**: LLM summarization
- **FastAPI**: Modern Python web framework

---

Built for financial intelligence automation