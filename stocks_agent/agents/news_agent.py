"""
News Agent - Fetches and analyzes news articles for stock sentiment.
Connects directly to MongoDB for faster access to news data.
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Add parent directory to path for direct script execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base import BaseAgent
from schemas.inputs import NewsInput
from schemas.outputs import NewsOutput
from state import StockAgentState

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import config first to ensure .env is loaded
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


class NewsAgent(BaseAgent):
    """
    Agent that analyzes news articles related to a stock ticker.
    
    Connects directly to MongoDB for news data from the news scraper pipeline.
    Falls back to REST API if MongoDB is unavailable.
    
    Input: ticker
    Output: news_output (list of articles), overall_sentiment, timestamp
    """
    
    name = "news_agent"
    description = "Analyzes news articles for stock sentiment analysis"
    input_schema = NewsInput
    output_schema = NewsOutput
    
    # MongoDB configuration
    MONGODB_URI = os.getenv('MONGODB_URI', os.getenv('NEWS_MONGODB_URI', ''))
    MONGODB_DB = os.getenv('MONGODB_DB', os.getenv('NEWS_MONGODB_DB', 'news_db'))
    
    # Fallback API URL (if MongoDB not configured)
    NEWS_API_URL = os.getenv('NEWS_API_URL', 'http://localhost:8000/api/news/summarized')
    
    def __init__(self):
        super().__init__()
        self._client = None
        self._mongo_client = None
        self._mongo_db = None
        self._use_mongodb = bool(self.MONGODB_URI)
        
        if self._use_mongodb:
            self._init_mongodb()
    
    def _init_mongodb(self):
        """Initialize MongoDB connection."""
        try:
            from pymongo import MongoClient
            self._mongo_client = MongoClient(
                self.MONGODB_URI,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=5,
                minPoolSize=1
            )
            # Test connection
            self._mongo_client.admin.command('ping')
            self._mongo_db = self._mongo_client[self.MONGODB_DB]
            logger.info(f"NewsAgent: Connected to MongoDB ({self.MONGODB_DB})")
        except Exception as e:
            logger.warning(f"NewsAgent: MongoDB connection failed: {e}. Falling back to API.")
            self._use_mongodb = False
            self._mongo_client = None
            self._mongo_db = None
    
    @property
    def client(self):
        """Lazy-load OpenAI client to avoid import errors when API key not set."""
        if self._client is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                from openai import OpenAI
                self._client = OpenAI()
            else:
                logger.warning("OPENAI_API_KEY not set, LLM sentiment analysis disabled")
        return self._client

    def _fetch_from_mongodb(self, ticker: str, limit: int = 50, hours: int = 72) -> List[Dict[str, Any]]:
        """
        Fetch news articles directly from MongoDB.
        
        Args:
            ticker: Company/stock ticker to search for (case-insensitive)
            limit: Maximum number of articles to return
            hours: How far back to search (in hours)
            
        Returns:
            List of news article dictionaries
        """
        if not self._mongo_db:
            return []
        
        try:
            # Calculate time cutoff
            since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
            
            # Query the summarize collection (LLM-processed articles)
            query = {
                'company': ticker.lower(),
                'is_relevant': True,  # Only relevant articles
            }
            
            # Try to filter by date if the field exists
            cursor = self._mongo_db.summarize.find(query).sort(
                'published_at', -1
            ).limit(limit)
            
            articles = list(cursor)
            
            # If no summarized articles, try enriched_articles
            if not articles:
                logger.info(f"No summarized articles found, trying enriched_articles...")
                cursor = self._mongo_db.enriched_articles.find({
                    'company': ticker.lower()
                }).sort('published_at', -1).limit(limit)
                articles = list(cursor)
            
            logger.info(f"MongoDB: Found {len(articles)} articles for {ticker}")
            return articles
            
        except Exception as e:
            logger.error(f"MongoDB query error: {e}")
            return []

    def _fetch_from_api(self, ticker: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch news articles from the REST API (fallback).
        
        Args:
            ticker: Company/stock ticker to search for
            limit: Maximum number of articles to return
            
        Returns:
            List of news article dictionaries
        """
        import requests
        
        try:
            params = {
                "company": ticker.lower(),
                "limit": limit,
                "skip": 0,
                "is_relevant": True
            }
            
            response = requests.get(self.NEWS_API_URL, params=params, timeout=10)
            response.raise_for_status()
            articles = response.json()
            
            if isinstance(articles, list):
                logger.info(f"API: Fetched {len(articles)} articles for {ticker}")
                return articles
            return []
            
        except Exception as e:
            logger.warning(f"API request failed: {e}")
            return []

    def _format_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a raw article into the expected news item format.
        
        Args:
            article: Raw article from MongoDB or API
            
        Returns:
            Formatted article dictionary
        """
        # Handle MongoDB ObjectId
        if '_id' in article:
            article['_id'] = str(article['_id'])
        
        # Extract summary - prefer LLM summary, fall back to content snippet
        summary = article.get('summary', '')
        if not summary:
            content = article.get('content', '')
            summary = content[:300] + '...' if len(content) > 300 else content
        
        # Extract sentiment info
        sentiment_label = article.get('sentiment_label', 'neutral')
        
        # Build impact info if available
        impact = article.get('impact_assessment', '')
        if not impact:
            liquidity_impact = article.get('liquidity_impact', '')
            if liquidity_impact:
                impact = f"Liquidity impact: {liquidity_impact}"
        
        return {
            "title": article.get('title', 'No Title'),
            "source": article.get('source', article.get('publisher_name', 'Unknown')),
            "summary": summary,
            "date": article.get('published_at', datetime.utcnow().isoformat()),
            "sentiment": sentiment_label,
            "impact": impact,
            "url": article.get('url', ''),
            "key_points": article.get('key_points', []),
            "financial_metrics": article.get('financial_metrics', {})
        }

    def get_overall_sentiment_from_llm(
        self,
        ticker: str,
        news_items: List[Dict[str, Any]]
    ) -> str:
        """
        Use an LLM to infer overall sentiment from news articles.

        Returns: one of "bullish", "bearish", "neutral".
        """
        if not news_items:
            return "neutral"
        
        # First, try to aggregate from article sentiments
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        for item in news_items:
            sentiment = item.get('sentiment', 'neutral').lower()
            if sentiment in sentiment_counts:
                sentiment_counts[sentiment] += 1
            elif 'positive' in sentiment or 'bullish' in sentiment:
                sentiment_counts['positive'] += 1
            elif 'negative' in sentiment or 'bearish' in sentiment:
                sentiment_counts['negative'] += 1
            else:
                sentiment_counts['neutral'] += 1
        
        # If clear majority, use that
        total = sum(sentiment_counts.values())
        if total > 0:
            if sentiment_counts['positive'] / total > 0.6:
                return "bullish"
            elif sentiment_counts['negative'] / total > 0.6:
                return "bearish"
        
        # Use LLM for more nuanced analysis
        if not self.client:
            logger.info("OpenAI client not available, using sentiment counts")
            if sentiment_counts['positive'] > sentiment_counts['negative']:
                return "bullish"
            elif sentiment_counts['negative'] > sentiment_counts['positive']:
                return "bearish"
            return "neutral"

        # Build article summary for prompt
        articles_text_parts = []
        for idx, item in enumerate(news_items[:10], start=1):  # Limit to 10 articles
            articles_text_parts.append(
                f"Article {idx}:\n"
                f"Title: {item.get('title', '')}\n"
                f"Source: {item.get('source', '')}\n"
                f"Summary: {item.get('summary', '')}\n"
                f"Sentiment: {item.get('sentiment', 'unknown')}\n"
                f"Impact: {item.get('impact', '')}\n"
            )
        articles_text = "\n\n".join(articles_text_parts)

        prompt = (
            f"You are an expert financial analyst.\n"
            f"Given the following news articles about the stock '{ticker}', "
            f"determine the overall market sentiment.\n\n"
            f"Classify sentiment as one word:\n"
            f"- bullish (positive, optimistic)\n"
            f"- bearish (negative, pessimistic)\n"
            f"- neutral (mixed or unclear)\n\n"
            f"Return ONLY: bullish, bearish, or neutral.\n\n"
            f"News Articles:\n{articles_text}"
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial news sentiment analyst. Respond with only one word."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0
            )
            sentiment_raw = response.choices[0].message.content.strip().lower()
            
            if "bullish" in sentiment_raw:
                return "bullish"
            elif "bearish" in sentiment_raw:
                return "bearish"
            else:
                return "neutral"
                
        except Exception as e:
            logger.error(f"Error calling LLM for sentiment: {e}")
            return "neutral"

    def run(self, input_data: Dict[str, Any], state: StockAgentState) -> Dict[str, Any]:
        """
        Fetches news and calculates sentiment.
        
        Args:
            input_data: Validated input parameters (contains 'ticker')
            state: Current agent state
            
        Returns:
            State update dictionary
        """
        # Extract ticker (input_data is a dict after validation)
        ticker = input_data.get('ticker', '')
        
        logger.info(f"NewsAgent: Processing {ticker}")
        
        limit = 50
        raw_articles = []
        
        # Try MongoDB first (faster, more data)
        if self._use_mongodb:
            raw_articles = self._fetch_from_mongodb(ticker, limit=limit)
        
        # Fallback to API if MongoDB didn't return results
        if not raw_articles:
            logger.info("Falling back to API...")
            raw_articles = self._fetch_from_api(ticker, limit=limit)
        
        # Format articles
        news_items: List[Dict[str, Any]] = []
        for article in raw_articles:
            try:
                formatted = self._format_article(article)
                news_items.append(formatted)
            except Exception as e:
                logger.warning(f"Error formatting article: {e}")
                continue
        
        # If still no articles, create mock data
        if not news_items:
            logger.warning(f"No news found for {ticker}, using mock data")
            news_items = [
                {
                    "title": f"[MOCK] No recent news available for {ticker}",
                    "source": "System",
                    "summary": "No news articles were found in the database or API.",
                    "date": datetime.utcnow().isoformat(),
                    "sentiment": "neutral",
                    "impact": "",
                    "url": "",
                    "key_points": [],
                    "financial_metrics": {}
                }
            ]
        
        logger.info(f"NewsAgent: Found {len(news_items)} articles for {ticker}")

        overall_sentiment = self.get_overall_sentiment_from_llm(ticker, news_items)

        # The Pydantic field is named 'news_output', so we must assign our list to that key.
        output = NewsOutput(
            news_output=news_items,  
            overall_sentiment=overall_sentiment,
            timestamp=datetime.utcnow().isoformat()
        )
        
        return {
            "news_output": output.model_dump(),
            "agent_contributions": [self.name]
        }

    def __del__(self):
        """Cleanup MongoDB connection on agent destruction."""
        if self._mongo_client:
            try:
                self._mongo_client.close()
            except Exception:
                pass


if __name__ == "__main__":
    # Test
    import json
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    test_input = {"ticker": "tcs"}
    agent = NewsAgent()
    
    print(f"\nMongoDB enabled: {agent._use_mongodb}")
    print(f"MongoDB URI: {'Set' if agent.MONGODB_URI else 'Not set'}")
    
    # Note: State is empty for local test
    response = agent.run(test_input, {})
    
    print("\n  Agent Output  ")
    print(json.dumps(response, indent=2, default=str))
