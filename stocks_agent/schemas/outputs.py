"""
Output schemas for each agent in the StocksAgent system.
Each agent produces structured output according to its schema.
"""

from typing import TypedDict, Optional, List, Dict, Any, Annotated, Literal, Tuple
from pydantic import BaseModel, Field
from datetime import datetime


class NewsOutput(BaseModel):
    """Output schema for the News Agent."""
    
    news_output: List = Field(
        default_factory=list,
        description="List of news articles with title, source, summary, sentiment"
    )
    overall_sentiment: str = Field(
        ..., 
        description="Overall sentiment: 'bullish', 'bearish', or 'neutral'"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of when analysis was performed"
    )


class TwitterOutput(BaseModel):
    """Output schema for the Twitter Agent."""
    
    summary: str = Field(..., description="Summary of Twitter sentiment and discussion")
    sentiment_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Sentiment score from 0 (bearish/negative) to 1 (bullish/positive)"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of when analysis was performed"
    )


class MontecarloOutput(BaseModel):
    """Output schema for the Montecarlo Agent."""
    
    results: Dict[str, Any] = Field(
        default_factory=dict,
        description="Monte Carlo simulation results with metrics like mean_return, var_95, etc."
    )


class TechnicalOutput(BaseModel):
    """
    Output schema for the Technical Analysis Agent, designed to capture 
    the aggregated results of indicator analysis.
    """
    
    # Identification and Status 
    status: Literal["success", "error"] = Field(
        ..., 
        description="The execution status of the technical analysis process."
    )
    ticker: str = Field(
        ..., 
        description="The stock ticker symbol or the name of the company"
    )
    
    # Summary Signal 
    signal: Literal["BUY", "SELL", "HOLD"] = Field(
        ...,
        description="The final aggregated trading decision based on all indicators."
    )
    strength: float = Field(
        ...,
        description="The confidence level of the final aggregated signal."
    )
    reason: str = Field(
        ...,
        description="A brief justification for the final signal, often referencing the dominant indicators."
    )
    # Metadata 
    json_data: Dict[str, Any] = Field(
        ...,
        description="A dictionary containing detailed indicator values and intermediate calculations."
    )
    timestamp: str = Field(
        ...,
        description="ISO 8601 formatted timestamp of when the analysis was completed."
    )

class FundamentalOutput(BaseModel):
    """Top-level output schema for the Fundamental Analysis Agent."""
    fundamental_output: Dict[str, Any] = Field(
        ...,
        description="Map of ticker -> raw DCF analysis or error text.",
    )
    agent_contributions: List[str] = Field(
        ...,
        description="List of agent names that contributed to this result.",
    )