"""
News Agent - Fetches and analyzes news articles for stock sentiment.
"""

import os
import sys
import logging
from typing import Dict, Any, List
from datetime import datetime

# Add parent directory to path for direct script execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

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
    
    Input: ticker
    Output: news_output (list of articles), overall_sentiment, timestamp
    """
    
    name = "news_agent"
    description = "Analyzes news articles for stock sentiment analysis"
    input_schema = NewsInput
    output_schema = NewsOutput
    
    def __init__(self):
        super().__init__()
        self._client = None
    
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
        
        if not self.client:
            logger.info("OpenAI client not available, returning neutral sentiment")
            return "neutral"

        # Build article summary for prompt
        articles_text_parts = []
        for idx, item in enumerate(news_items[:10], start=1):  # Limit to 10 articles
            articles_text_parts.append(
                f"Article {idx}:\n"
                f"Title: {item.get('title', '')}\n"
                f"Source: {item.get('source', '')}\n"
                f"Summary: {item.get('summary', '')}\n"
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
        
        # Using ticker directly as requested
        api_url = "http://136.119.40.138:8000/api/news/summarized"
        params = {
            "company": ticker,
            "limit": limit,
            "skip": 0
        }

        news_items: List[Dict[str, Any]] = []
        
        try:
            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            api_data = response.json()
            
            if isinstance(api_data, list):
                for article in api_data:
                    item = {
                        "title": article.get("title", "No Title"),
                        "source": article.get("source", "Unknown Source"),
                        "summary": article.get("content", "")[:200] + "...",
                        "date": article.get("published_at", datetime.utcnow().isoformat())
                    }
                    news_items.append(item)
                    
            logger.info(f"Fetched {len(news_items)} news articles")
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error calling News API: {e}")
            # Use mock data as fallback
            news_items = [
                {
                    "title": f"[MOCK] {ticker} shows strong performance",
                    "source": "Mock News",
                    "summary": "This is mock news data. News API unavailable.",
                    "date": datetime.utcnow().isoformat()
                }
            ]

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


if __name__ == "__main__":
    # Test
    test_input = {"ticker": "TATACONSUM"}
    agent = NewsAgent()
    # Note: State is empty for local test
    response = agent.run(test_input, {})
    
    import json
    print("\n  Agent Output  ")
    print(json.dumps(response, indent=2))
