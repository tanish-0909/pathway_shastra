"""
Native MongoDB Streaming Pipeline
- Polls MongoDB for new raw articles
- Real-time message-by-message processing
- High throughput with asyncio concurrency
- Writes enriched articles directly to MongoDB
"""

import asyncio
import hashlib
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any

import redis
from pymongo import MongoClient

from dedup import DeduplicationManager
from features import extract_features
from fetcher import fetch_article
from sentiment import FinBERTAnalyzer
from storage import StorageHandler

# ===========================
# Logging
# ===========================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===========================
# Configuration
# ===========================

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))

MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGO_DB = os.getenv('MONGODB_DB', 'news_db')

MAX_CONCURRENT = int(os.getenv('MAX_CONCURRENT_FETCHES', '20'))
POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', '5'))  # seconds

# ===========================
# Global Components
# ===========================

redis_client = None
dedup_manager = None
sentiment_analyzer = None
storage = None
mongo_db = None

# ===========================
# Cluster ID Generator
# ===========================

def generate_cluster_id(title_normalized: str, company: str, factor_type: str, published_at: str) -> str:
    """Generate cluster ID from article attributes"""
    day = published_at[:10] if published_at else datetime.utcnow().strftime('%Y-%m-%d')
    title_key = title_normalized[:50] if title_normalized else 'untitled'
    title_hash = hashlib.md5(title_key.encode()).hexdigest()[:8]
    return f"cluster_{company}_{factor_type}_{day}_{title_hash}"

# ===========================
# Processing Function
# ===========================

async def process_article(message: Dict[str, Any]) -> bool:
    """Process a single article through the enrichment pipeline"""
    global dedup_manager, sentiment_analyzer, storage, mongo_db
    
    article_id = message.get('article_id')
    title = message.get('title', '')
    url = message.get('url', '')
    source = message.get('source', '')
    published_at = message.get('published_at', '')
    company = message.get('company', '')
    factor_type = message.get('factor_type', '')
    scraped_at = message.get('scraped_at', '')
    
    try:
        # Normalize title early for dedup
        title_normalized = dedup_manager.normalize_title(title)
        
        # STEP 1: URL Dedup
        url_dup, url_hash = dedup_manager.is_url_duplicate(url)
        if url_dup:
            logger.info(f"URL duplicate: {company} - {title[:40]}...")
            return True  # Mark as processed
        
        # STEP 2: Fetch Content
        fetch_result = await fetch_article(url)
        
        content = fetch_result.get('content') or title
        final_url = fetch_result.get('final_url') or url
        publisher_name = fetch_result.get('publisher_name')
        author = fetch_result.get('author')
        published_date = fetch_result.get('published_date')
        publisher_icon = fetch_result.get('publisher_icon')
        
        # STEP 3: Content Dedup
        if content and len(content) >= 100:
            content_dup, content_hash = dedup_manager.is_content_duplicate(content)
            if content_dup:
                logger.info(f"Content duplicate: {company} - {title[:40]}...")
                return True  # Mark as processed
        else:
            content_hash = ""
        
        # STEP 4: Fuzzy Title Dedup
        title_dup, existing_cluster = dedup_manager.is_title_duplicate(
            title, company, published_at
        )
        if title_dup and existing_cluster:
            logger.info(f"Title duplicate -> cluster {existing_cluster[:8]}: {source} - {title[:35]}...")
            
            # Update cluster with this new publisher
            storage.update_cluster(
                cluster_id=existing_cluster,
                article={'title': title, 'company': company},
                publisher_info={
                    'name': publisher_name or source,
                    'icon': publisher_icon,
                    'url': final_url,
                    'source': source,
                    'published_at': published_at,
                    'title_normalized': title_normalized
                }
            )
            return True  # Mark as processed
        
        # STEP 5: Content Quality Check
        content_quality = 'good'
        if not content or len(content) < 200:
            content_quality = 'poor'
            logger.warning(f"Poor content quality ({len(content) if content else 0} chars): {company} - {title[:40]}...")
        
        # STEP 6: Sentiment Analysis (with title fallback for poor content)
        text_for_sentiment = f"{title}. {content[:2000]}" if content else title
        sentiment = sentiment_analyzer.analyze(text_for_sentiment, title=title)
        
        # STEP 7: Feature Extraction
        features = extract_features(title, content, sentiment, factor_type)
        
        # STEP 8: Generate Cluster ID
        cluster_id = generate_cluster_id(
            title_normalized, company, factor_type, published_at
        )
        
        # STEP 9: Register in Dedup Index
        dedup_manager.register_article(
            url_hash=url_hash,
            content_hash=content_hash,
            title=title,
            company=company,
            published_at=published_at,
            cluster_id=cluster_id
        )
        
        # STEP 10: Build Enriched Document
        enriched = {
            'article_id': article_id,
            'title': title,
            'title_normalized': title_normalized,
            'url': final_url,
            'original_url': url,
            'url_hash': url_hash,
            'source': source,
            'published_at': published_at,
            'scraped_at': scraped_at,
            'company': company,
            'factor_type': factor_type,
            'content': content,
            'content_hash': content_hash,
            'content_length': len(content) if content else 0,
            'content_quality': content_quality,
            'publisher_name': publisher_name,
            'published_date': published_date,
            'author': author,
            'publisher_icon': publisher_icon,
            'sentiment_label': sentiment['label'],
            'sentiment_score': sentiment['score'],
            'sentiment_confidence': sentiment['confidence'],
            'liquidity_impact': features['liquidity_impact'],
            'critical_events': ','.join(features['critical_events']),
            'decisions': ','.join(features['decisions']),
            'cluster_id': cluster_id,
            'enriched_at': datetime.utcnow().isoformat(),
            'summarized': False  # Flag for LLM worker to pick up
        }
        
        # STEP 11: Store in MongoDB
        storage.store_article(enriched)
        storage.update_cluster(
            cluster_id=cluster_id,
            article=enriched,
            publisher_info={
                'name': publisher_name or source,
                'icon': publisher_icon,
                'url': final_url,
                'source': source,
                'published_at': published_at,
                'title_normalized': title_normalized
            }
        )
        
        logger.info(f"UNIQUE enriched: {company} - {title[:40]}... [{sentiment['label']}/{features['liquidity_impact']}]")
        return True
        
    except Exception as e:
        logger.error(f"Error processing {article_id}: {e}")
        return False

# ===========================
# Main Pipeline
# ===========================

async def run_pipeline():
    """Main streaming pipeline - polls MongoDB for new articles"""
    global redis_client, dedup_manager, sentiment_analyzer, storage, mongo_db
    
    logger.info("=" * 60)
    logger.info("Native Streaming Pipeline - Starting (MongoDB Direct)")
    logger.info("=" * 60)
    
    # Initialize components
    logger.info("Initializing components...")
    
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=False,
        socket_connect_timeout=5
    )
    redis_client.ping()
    logger.info(f"Redis connected: {REDIS_HOST}:{REDIS_PORT}")
    
    dedup_manager = DeduplicationManager(redis_client)
    sentiment_analyzer = FinBERTAnalyzer()
    storage = StorageHandler(MONGO_URI, MONGO_DB)
    
    # Connect to MongoDB for polling raw articles
    mongo_client = MongoClient(
        MONGO_URI,
        maxPoolSize=10,
        minPoolSize=2,
        maxIdleTimeMS=300000,
        waitQueueTimeoutMS=5000,
        connectTimeoutMS=10000,
        socketTimeoutMS=30000
    )
    mongo_db = mongo_client[MONGO_DB]
    raw_articles = mongo_db['raw_articles']
    
    logger.info("All components initialized")
    
    logger.info("=" * 60)
    logger.info("Pipeline Architecture:")
    logger.info("  1. MongoDB (raw_articles) - Poll for new articles")
    logger.info("  2. Redis dedup check (URL -> Content -> Fuzzy Title)")
    logger.info("  3. Fetch article content (aiohttp/Playwright)")
    logger.info("  4. FinBERT sentiment analysis")
    logger.info("  5. Feature extraction")
    logger.info("  6. MongoDB storage (enriched_articles)")
    logger.info("=" * 60)
    logger.info("Pipeline ready - polling for messages...")
    logger.info("=" * 60)
    
    # Semaphore for concurrency control
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    
    processed_count = 0
    
    try:
        while True:
            # Find unprocessed articles
            unprocessed = list(raw_articles.find({'processed': False}).limit(50))
            
            if not unprocessed:
                logger.debug(f"No unprocessed articles, sleeping {POLL_INTERVAL}s...")
                await asyncio.sleep(POLL_INTERVAL)
                continue
            
            logger.info(f"Found {len(unprocessed)} unprocessed articles")
            
            async def process_with_semaphore(article):
                async with semaphore:
                    success = await process_article(article)
                    if success:
                        # Mark as processed in MongoDB
                        raw_articles.update_one(
                            {'_id': article['_id']},
                            {'$set': {'processed': True, 'processed_at': datetime.utcnow()}}
                        )
                    return success
            
            # Process all articles concurrently
            tasks = [process_with_semaphore(article) for article in unprocessed]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful = sum(1 for r in results if r is True)
            processed_count += successful
            
            logger.info(f"Processed {successful}/{len(unprocessed)} articles (total: {processed_count})")
    
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
    finally:
        mongo_client.close()
        logger.info("Pipeline stopped")

# ===========================
# Entry Point
# ===========================

if __name__ == "__main__":
    asyncio.run(run_pipeline())
