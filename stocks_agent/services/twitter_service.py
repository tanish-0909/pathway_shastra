"""
Twitter Service Module.

Handles Twitter API interactions and MongoDB caching for sentiment data.
Extracted from twitter_agent.py for reusability.
"""

import sys
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime

# Import config first to ensure .env is loaded
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config

import requests

logger = logging.getLogger(__name__)


MONGO_URI = os.getenv("MONGO_URI")

class TwitterAPIService:
    """
    Service for fetching tweets from Twitter API.
    """
    
    API_URL = "https://api.twitterapi.io/twitter/tweet/advanced_search"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Twitter API service.
        
        Args:
            api_key: Twitter API key (defaults to TWITTER_API_KEY env var)
        """
        self.api_key = api_key or os.environ.get("TWITTER_API_KEY")
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    @property
    def is_configured(self) -> bool:
        """Check if API key is set."""
        return bool(self.api_key)
    
    def fetch_tweets(
        self, 
        ticker: str, 
        hours_delta: float = 24,
        query_type: str = "Top",
        company_name: Optional[str] = None
    ) -> List[Dict]:
        """
        Fetch tweets for a ticker from the API.
        
        Args:
            ticker: Stock ticker symbol
            hours_delta: Time window in hours
            query_type: Type of query (Top, Latest, etc.)
            
        Returns:
            List of tweet dictionaries
        """
        if not self.is_configured:
            logger.warning("Twitter API key not configured")
            return []
        
        
        ticker_query = f"{ticker} OR ${ticker}"
        if company_name and type(company_name)==str:
            ticker_query += f" OR {company_name}"
        
        try:
            logger.info(f"Fetching tweets for {ticker} (last {hours_delta}h)...")
            
            params = {
                "query": f"({ticker_query}) within_time:{int(hours_delta)}h filter:news",
                "queryType": query_type
            }
            
            response = requests.get(
                self.API_URL, 
                headers=self.headers, 
                params=params, 
                timeout=20
            )
            response.raise_for_status()
            data = response.json()
            
            tweets_list = []
            if "tweets" in data:
                for tweet in data["tweets"]:
                    try:
                        # Skip ads
                        if "ads" in tweet.get("source", "").lower():
                            continue
                        
                        tweet_obj = {
                            "_id": tweet["id"],
                            "ticker": ticker,
                            "hours_delta": hours_delta,
                            "text": tweet.get("text", ""),
                            "createdAt": tweet.get("createdAt", ""),
                            "author": tweet.get("author", {})
                        }
                        tweets_list.append(tweet_obj)
                    except KeyError:
                        continue
            
            logger.info(f"Fetched {len(tweets_list)} tweets for {ticker}")
            return tweets_list
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Twitter API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching tweets: {e}")
            return []


class TwitterDatabase:
    """
    MongoDB handler for Twitter sentiment data caching.
    """
    
    def __init__(
        self, 
        mongo_uri: Optional[str] = None,
        db_name: str = "TwitterAnalytics"
    ):
        """
        Initialize the database connection.
        
        Args:
            mongo_uri: MongoDB connection URI (defaults to MONGO_URI env var)
            db_name: Database name
        """
        self.mongo_uri = mongo_uri or MONGO_URI
        self.db_name = db_name
        self.client = None
        self.db = None
        self.sentiment_col = None
        
        self._connect()
    
    def _connect(self):
        """Establish database connection."""
        try:
            from pymongo import MongoClient
            
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=2000)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.sentiment_col = self.db["SentimentAnalysis"]
            logger.info("Connected to MongoDB successfully")
        except ImportError:
            logger.warning("pymongo not installed. Database caching disabled.")
            self.client = None
        except Exception as e:
            logger.warning(f"Database connection failed: {e}")
            self.client = None
    
    @property
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self.client is not None
    
    def save_analysis(self, analysis_doc: Dict) -> bool:
        """
        Save sentiment analysis to database.
        
        Args:
            analysis_doc: Document to save
            
        Returns:
            True if successful, False otherwise
        """
        
        if not self.is_connected:
            return False
        
        try:
            self.sentiment_col.insert_one(analysis_doc)
            logger.debug(f"Saved sentiment report for {analysis_doc.get('ticker')}")
            return True
        except Exception as e:
            logger.error(f"Failed to save analysis: {e}")
            return False
    
    def get_latest_sentiment(self, ticker: str) -> Optional[Dict]:
        """
        Get the most recent sentiment analysis for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Latest sentiment document or None
        """
        if not self.is_connected:
            return None
        
        try:
            return self.sentiment_col.find_one(
                {"ticker": ticker},
                sort=[("timestamp", -1)]
            )
        except Exception as e:
            logger.error(f"Failed to fetch sentiment: {e}")
            return None
    
    def get_sentiment_history(
        self, 
        ticker: str, 
        limit: int = 10
    ) -> List[Dict]:
        """
        Get sentiment history for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            limit: Maximum documents to return
            
        Returns:
            List of sentiment documents
        """
        if not self.is_connected:
            return []
        
        try:
            cursor = self.sentiment_col.find(
                {"ticker": ticker}
            ).sort("timestamp", -1).limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"Failed to fetch sentiment history: {e}")
            return []

