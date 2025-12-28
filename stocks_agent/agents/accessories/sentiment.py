"""
Sentiment Analysis Core Module.

Contains LLM-based sentiment analysis logic for social media data.
Extracted from twitter_agent.py for reusability.
"""

import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Core class for analyzing sentiment from social media data using LLMs.
    """
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0):
        """
        Initialize the sentiment analyzer.
        
        Args:
            model: OpenAI model to use
            temperature: LLM temperature setting
        """
        self.model = model
        self.temperature = temperature
        self._llm = None
    
    @property
    def llm(self):
        """Lazy-load the LLM to avoid import errors when not needed."""
        if self._llm is None:
            try:
                from langchain_openai import ChatOpenAI
                self._llm = ChatOpenAI(model=self.model, temperature=self.temperature)
            except ImportError:
                raise ImportError(
                    "langchain-openai is required for sentiment analysis. "
                    "Install with: pip install langchain-openai"
                )
        return self._llm
    
    @staticmethod
    def format_tweets_for_llm(tweets_data: List[Dict]) -> str:
        """
        Format tweet objects into a string for the LLM.
        
        Args:
            tweets_data: List of tweet dictionaries
            
        Returns:
            Formatted string for LLM input
        """
        if not tweets_data:
            return "No tweet data available."
        
        formatted_text = "RECENT TWEETS:\n"
        try:
            for i, tweet in enumerate(tweets_data, 1):
                text = tweet.get('text', '').replace('\n', ' ')
                author = tweet.get('author', {})
                username = author.get('userName', 'Unknown')
                is_blue = author.get('isBlueVerified', False)
                author_verified = "BlueVerified" if is_blue else "Unverified"
                
                formatted_text += f"{i}. [User={username}, {author_verified}] [tweet={text}]\n"
        except Exception as e:
            return f"Error formatting tweets: {e}"
        
        return formatted_text
    
    def analyze_tweets(
        self, 
        ticker: str, 
        tweets_list: List[Dict], 
        hours_delta: float
    ) -> Dict:
        """
        Run sentiment analysis on tweets using LLM.
        
        Args:
            ticker: Stock ticker symbol
            tweets_list: List of tweet dictionaries
            hours_delta: Time window in hours
            
        Returns:
            Dict with 'score' (0-1) and 'summary' keys
        """
        from langchain_core.messages import HumanMessage, SystemMessage
        
        logger.info(f"Running sentiment analysis on {len(tweets_list)} tweets for {ticker}...")
        
        try:
            tweets_text = self.format_tweets_for_llm(tweets_list)
            
            system_prompt = (
                "You are a senior financial analyst. Your job is to analyze raw X/Twitter data "
                "to determine the current market sentiment for a specific company's stocks."
            )
            
            user_prompt = f"""
            Analyze the following recent tweets regarding the ticker '{ticker}' in the last {hours_delta}h.
            
            Focus on:
            1. **Sentiment**: Is the chatter Bullish, Bearish, or Neutral?
            2. **Key Narratives**: What specific news or rumors are driving the conversation?
            3. **Credibility**: prioritize tweets from verified accounts.
            
            Return only this output in a single JSON block containing 2 key-values pairs:
                1) "score": <float between 0.0 (bearish) and 1.0 (bullish)>
                2) "summary": <string summary of analysisn with a strict word limit of 30 words> 
            
            {tweets_text}
            """
            
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            content = response.content.replace("```json", "").replace("```", "").strip()
            result_json = json.loads(content)
            return result_json
        
        except Exception as e:
            logger.error(f"LLM/Parsing Error: {e}")
            return {"score": 0.5, "summary": f"Error analyzing sentiment: {str(e)}"}
    
    def analyze_news(
        self,
        ticker: str,
        news_items: List[Dict]
    ) -> Dict:
        """
        Run sentiment analysis on news articles.
        
        Args:
            ticker: Stock ticker symbol
            news_items: List of news article dictionaries
            
        Returns:
            Dict with 'score' (0-1) and 'summary' keys
        """
        from langchain_core.messages import HumanMessage, SystemMessage
        
        logger.info(f"Running sentiment analysis on {len(news_items)} news items for {ticker}...")
        
        try:
            # Format news items
            news_text = "RECENT NEWS:\n"
            for i, item in enumerate(news_items, 1):
                title = item.get('title', 'No title')
                source = item.get('source', 'Unknown')
                summary = item.get('summary', '')[:200]
                news_text += f"{i}. [{source}] {title}\n   {summary}\n"
            
            system_prompt = (
                "You are a senior financial analyst. Analyze the news articles "
                "to determine overall market sentiment for the stock."
            )
            
            user_prompt = f"""
            Analyze the following news articles for ticker '{ticker}'.
            
            Return only a JSON with:
            1) "score": <float between 0.0 (bearish) and 1.0 (bullish)>
            2) "summary": <brief summary of sentiment and key themes>
            
            {news_text}
            """
            
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            content = response.content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        
        except Exception as e:
            logger.error(f"News sentiment analysis error: {e}")
            return {"score": 0.5, "summary": f"Error analyzing news: {str(e)}"}