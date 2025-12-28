"""
Input schemas for each agent in the StocksAgent system.
Each agent has unique input requirements.
"""

from typing import TypedDict, Optional, List, Dict, Any, Annotated, Literal, Tuple
from pydantic import BaseModel, Field


class NewsInput(BaseModel):
    """Input schema for the News Agent."""
    ticker: str = Field(..., description="Stock ticker symbol (e.g., 'AAPL')")

class TwitterInput(BaseModel):
    """Input schema for the Twitter Agent."""
    ticker: str = Field(..., description="Stock ticker symbol (e.g., 'AAPL')")
    hours_delta: float = Field(..., description="How much hours previously to do Twitter sentiment analysis from(numeric)")


class MontecarloInput(BaseModel):
    """Input schema for the Montecarlo Agent."""
    ticker: str = Field(..., description="Stock ticker symbol (e.g., 'AAPL')")
    days_history: int = Field(
        default=100,
        description="Number of historical days to use for simulation"
    )
    simulation_days: int = Field(
        default=15,
        description="Number of days to simulate forward"
    )
    num_simulations: int = Field(
        default=1_000_000,
        description="Number of Monte Carlo simulation paths"
    )
    mode: str = Field(
        default="real",
        description="Execution mode: 'mock' for testing, 'real' for live data"
    )


class TechnicalInput(BaseModel):
    """Input schema for the Technical Analysis Agent."""
    ticker: str = Field(
        ..., 
        description="Stock ticker symbol or the name of the company"
    )
    interval: str = Field(
        default="5minute", 
        description="The time interval for the data (e.g., '1minute', '5minute', '60minute', 'day')"
    )
    start_date: Optional[str] = Field(
        default=None, 
        description="Start date/time in ISO format (YYYY-MM-DDTHH:MM:SS)"
    )
    end_date: Optional[str] = Field(
        default=None, 
        description="End date/time in ISO format (YYYY-MM-DDTHH:MM:SS)"
    )

class FundamentalInput(BaseModel):
    """Input schema for the Fundamental Analysis Agent."""
    tickers: List[str] = Field(
        ...,
        description="List of stock ticker symbols / company names to analyze",
    )

