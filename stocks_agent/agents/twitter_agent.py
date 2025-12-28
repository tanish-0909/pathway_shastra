"""
Twitter Agent - Analyzes Twitter/X sentiment for stocks.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Add parent directory to path for direct script execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base import BaseAgent
from schemas.inputs import TwitterInput
from schemas.outputs import TwitterOutput
from state import StockAgentState
from services.twitter_service import TwitterAPIService, TwitterDatabase
from agents.accessories.sentiment import SentimentAnalyzer


logger = logging.getLogger(__name__)


class TwitterAgent(BaseAgent):
    """
    Agent that analyzes Twitter/X sentiment for a stock ticker.
    
    Uses:
    - services.twitter_service.TwitterAPIService for fetching tweets
    - services.twitter_service.TwitterDatabase for caching
    - core.sentiment.SentimentAnalyzer for LLM analysis
    
    Input: ticker, date (or hours_delta)
    Output: summary, sentiment_score, timestamp
    """
    
    name = "twitter_agent"
    description = "Analyzes Twitter/X sentiment for stocks using Live API or Cached DB"
    input_schema = TwitterInput
    output_schema = TwitterOutput
    
    def __init__(self):
        super().__init__()
        self.api_service = TwitterAPIService()
        self.db = TwitterDatabase()
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def _fetch_and_analyze(
        self, 
        ticker: str, 
        hours_delta: float,
        company_name: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Fetch fresh tweets and analyze sentiment.
        
        Args:
            ticker: Stock ticker symbol
            hours_delta: Time window in hours
            
        Returns:
            Analysis document or None if failed
        """
        try:
            # Fetch tweets
            tweets_list = self.api_service.fetch_tweets(ticker, hours_delta, company_name=company_name)
            
            if not tweets_list:
                logger.info(f"No tweets found for {ticker}")
                return None
            
            # Analyze sentiment
            sentiment_result = self.sentiment_analyzer.analyze_tweets(
                ticker, tweets_list, hours_delta
            )
            
            # Create analysis document
            analysis_doc = {
                "ticker": ticker,
                "timestamp": datetime.utcnow().isoformat(),
                "sentiment_score": sentiment_result.get("score", 0.5),
                "summary": sentiment_result.get("summary", ""),
                "tweet_count": len(tweets_list),
                "source": "live_api"
            }
            
            # Cache in database
            self.db.save_analysis(analysis_doc)
            
            return analysis_doc
        
        except Exception as e:
            logger.error(f"Failed to fetch/analyze tweets: {e}")
            return None
    
    def run(self, input_data: Dict[str, Any], state: StockAgentState) -> Dict[str, Any]:
        """
            Execute the Twitter Agent Logic.
            
            1. Try to fetch fresh data via API
            2. If API fails, try cached data from MongoDB
            3. Return structured output
            
            Args:
                input_data: Validated input parameters
                state: Current agent state
                
            Returns:
                State update dictionary
        """
        # Extract parameters (input_data is a dict after validation)
        ticker = input_data.get("ticker", "")
        hours_delta = input_data.get("hours_delta", 24)
        
        # Also check for date and convert to hours_delta if needed
        if "date" in input_data and not hours_delta:
            # Default to 24h if only date provided
            hours_delta = 24
        
        logger.info(f"TwitterAgent: Processing {ticker} (Last {hours_delta}h)")
        
        result_doc = None
        
        # 1. Try Fresh Data
        if self.api_service.is_configured:
            company_name = state.get("parsed_intent", {}).get("company_names", [None])[0]
            result_doc = self._fetch_and_analyze(ticker, hours_delta, company_name=company_name)
        else:
            logger.info("Twitter API not configured, skipping live fetch")
        
        # 2. Fallback to MongoDB cache
        if not result_doc and self.db.is_connected:
            logger.info(f"Falling back to MongoDB cache for {ticker}")
            cached_doc = self.db.get_latest_sentiment(ticker)
            if cached_doc:
                result_doc = {
                    "sentiment_score": cached_doc.get("sentiment_score", 0.5),
                    "summary": f"[CACHED - {cached_doc.get('timestamp')}] {cached_doc.get('summary', '')}",
                    "timestamp": cached_doc.get("timestamp", datetime.utcnow().isoformat())
                }
        
        # 3. Total Failure Fallback - Mock response
        if not result_doc:
            logger.info("Using mock Twitter sentiment data")
            result_doc = {
                "sentiment_score": 0.5,  # Slightly positive default
                "summary": (
                    f"Unable to fetch twitter data."
                ),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # 4. Create Output
        output = TwitterOutput(
            summary=str(result_doc.get("summary", "")),
            sentiment_score=float(result_doc.get("sentiment_score", 0.5)),
            timestamp=str(result_doc.get("timestamp", datetime.utcnow().isoformat()))
        )
        
        return {
            "twitter_output": output.model_dump(),
            "agent_contributions": [self.name]
        }


if __name__ == "__main__":
    # Test
    test_input = {"ticker": "NVDA", "hours_delta": 24}
    agent = TwitterAgent()
    response = agent.run(test_input, {})
    
    import json
    print("\n  Agent Output  ")
    print(json.dumps(response, indent=2))
