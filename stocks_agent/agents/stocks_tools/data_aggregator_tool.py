import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
from pymongo import MongoClient
from langchain_core.tools import tool
from pathlib import Path
import sys
current_file = Path(os.path.abspath(__file__))
parent_dir = current_file.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))
from google_search_tool import get_google_results

from dotenv import load_dotenv
load_dotenv()
# Configuration
MONGO_URI = os.getenv("MONGO_URI")
TWITTER_DB_NAME=os.getenv("TWITTER_DB_NAME", "TwitterAnalytics")
TWITTER_COLLECTION = os.getenv("TWITTER_COLLECTION", "SentimentAnalysis")
TECHNICAL_DB_NAME = os.getenv("TECHNICAL_DB_NAME", "indicator_signals")
TECHNICAL_COLLECTION = os.getenv("TECHNICAL_COLLECTION", "indicators")
NEWS_API_URL = os.getenv("NEWS_API_URL", "http://136.119.40.138:8000/api/news/summarized")

logger = logging.getLogger(__name__)

# Helper Functions
def _get_mongo_client():
    """Establishes a MongoDB connection."""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        return client
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        return None

def _fetch_twitter_data(client, ticker: str) -> Dict[str, Any]:
    """Fetches the latest Twitter sentiment for a ticker from MongoDB."""
    if not client:
        return {"error": "Database unavailable"}
    
    try:
        db = client[TWITTER_DB_NAME]
        col = db[TWITTER_COLLECTION]
        # Fetch latest document based on timestamp
        doc = col.find_one(
            {"ticker": ticker},
            sort=[("timestamp", -1)]
        )
        if doc:
            # Convert ObjectId to string for JSON serialization
            doc["_id"] = str(doc["_id"])
            return doc
        return {"status": "No twitter data found"}
    except Exception as e:
        logger.error(f"Error fetching Twitter data for {ticker}: {e}")
        return {"error": str(e)}

def _fetch_technical_data(client, ticker: str) -> Dict[str, Any]:
    """Fetches the latest Technical indicators for a ticker from MongoDB."""
    if not client:
        return {"error": "Database unavailable"}
    
    try:
        db = client[TECHNICAL_DB_NAME]
        col = db[TECHNICAL_COLLECTION]
        # Fetch latest document based on date/timestamp
        doc = col.find_one(
            {"ticker": ticker},
            sort=[("date", -1)]
        )
        if doc:
            doc["_id"] = str(doc["_id"])
            return doc
        return {"status": "No technical data found"}
    except Exception as e:
        logger.error(f"Error fetching Technical data for {ticker}: {e}")
        return {"error": str(e)}

def _fetch_news_data(ticker: str) -> Dict[str, Any]:
    """Fetches news summaries from the external API."""
    params = {
        "company": ticker,
        "limit": 5, # Limit to 5 recent articles
        "skip": 0
    }
    try:
        response = requests.get(NEWS_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {"articles": data, "count": len(data) if isinstance(data, list) else 0}
    except Exception as e:
        logger.error(f"Error fetching News data for {ticker}: {e}")
        return {"error": "News API unavailable or failed", "details": str(e)}

# The Tool Definition

@tool
def aggregate_stock_data(tickers: Optional[List[str]] = None, query: str = "") -> Dict[str, Any]:
    """
    Aggregates Twitter sentiment, News articles, and Technical indicators for a list of stock tickers.
    
    Args:
        tickers: A list of stock ticker symbols (e.g., ["RELIANCE", "TCS"]). 
                 If None or empty, uses a google search to give error.
                 
    Returns:
        A dictionary containing aggregated data for each requested ticker.
    """
    
    # If no tickers provided, default to a google search
    if not tickers:
        google_results = get_google_results(query)
        return {"google_search_results": google_results}
    
    results = {}
    mongo_client = _get_mongo_client()
    
    for ticker in tickers:
        logger.info(f"Aggregating data for: {ticker}")
        
        # 1. Fetch Twitter Data (MongoDB)
        twitter_data = _fetch_twitter_data(mongo_client, ticker)
        
        # 2. Fetch Technical Data (MongoDB)
        technical_data = _fetch_technical_data(mongo_client, ticker)
        
        # 3. Fetch News Data (API)
        news_data = _fetch_news_data(ticker)
        
        results[ticker] = {
            "timestamp": datetime.utcnow().isoformat(),
            "twitter_sentiment": twitter_data,
            "technical_indicators": technical_data,
            "news_summary": news_data
        }
        
    if mongo_client:
        mongo_client.close()
        
    return results


if __name__ == "__main__":
    from unittest.mock import patch, MagicMock
    import json

    print("="*60)
    print("TESTING AGGREGATE TOOL (ZERO TICKER LOGIC)")
    print("="*60)

    # We mock 'get_google_results' so we don't need real API keys or the external file for this test
    # We use patch on the module name where it is imported. 
    # Since we are in the same file, we patch the name in the local namespace.
    with patch(f'{__name__}.get_google_results') as mock_search:
        
        # 1. Setup the Mock Return Value
        mock_search.return_value = [
            {
                "title": "Global Markets Rally",
                "link": "http://finance.example.com",
                "snippet": "Major indices are up 2% following inflation data."
            },
            {
                "title": "Tech Sector Analysis",
                "link": "http://tech.example.com",
                "snippet": "AI stocks continue to drive market momentum."
            }
        ]

        # 2. Define Inputs
        test_tickers = [] # Empty list to trigger fallback
        test_query = "What is the general market sentiment today?"

        print(f"Input Tickers: {test_tickers}")
        print(f"Input Query:   '{test_query}'\n")

        # 3. Run the Tool
        try:
            result = aggregate_stock_data.invoke({"tickers":test_tickers, "query":test_query})

            # 4. Verify Results
            if "google_search_results" in result:
                print("SUCCESS: Fallback to Google Search triggered.")
                print("  Output  ")
                print(json.dumps(result, indent=2))
                
                # Verify the mock was actually called
                mock_search.assert_called_once_with(test_query)
                print("\n(Verified that get_google_results was called exactly once)")
            else:
                print("FAILURE: Did not find 'google_search_results' in output.")
                print(result)

        except Exception as e:
            print(f"ERROR: An exception occurred: {e}")

    print("="*60)