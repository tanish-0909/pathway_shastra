"""
Kafka message schemas for StocksAgent.

Pydantic models for trade signals and stock analysis messages.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class TradeSignal(BaseModel):
    """
    Schema for trade signals from indicators_refactored pipeline.
    Published to 'trade_signals' Kafka topic.
    """
    ticker: str = Field(..., description="Stock ticker symbol")
    date: str = Field(..., description="Signal timestamp")
    close_price: float = Field(..., description="Current close price")
    open_price: float = Field(..., description="Current open price")
    volume: float = Field(..., description="Trading volume")
    action: str = Field(..., description="Trading action: BUY, SELL, or HOLD")
    stop_loss: float = Field(default=0.0, description="Stop loss price")
    take_profit: float = Field(default=0.0, description="Take profit price")
    signal_strength: float = Field(default=0.0, description="Signal strength score")
    limit_order: float = Field(default=0.0, description="Limit order price")
    current_price: float = Field(..., description="Current market price")
    
    # Technical indicators
    rsi: float = Field(default=0.0, description="RSI value")
    macd: float = Field(default=0.0, description="MACD value")
    macd_signal: float = Field(default=0.0, description="MACD signal line")
    macd_hist: float = Field(default=0.0, description="MACD histogram")
    vwap: float = Field(default=0.0, description="VWAP value")
    bol_bands: List[float] = Field(default_factory=lambda: [0.0, 0.0], description="Bollinger bands")
    sma: List[float] = Field(default_factory=lambda: [0.0, 0.0], description="SMA values")
    crsi: float = Field(default=0.0, description="Connors RSI")
    klinger: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0], description="Klinger oscillator")
    keltner: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0], description="Keltner channels")
    cmo: float = Field(default=0.0, description="Chande Momentum Oscillator")
    reason: str = Field(default="", description="Signal reasoning")
    
    # Optional metadata
    time: Optional[int] = Field(default=None, description="Unix timestamp")
    diff: Optional[int] = Field(default=None, description="Diff value")
    
    class Config:
        extra = "allow"  # Allow additional fields


class StockAnalysis(BaseModel):
    """
    Schema for stock analysis output from stocksagent.
    Published to 'stock_analysis' Kafka topic.
    """
    message_type: str = Field(default="technical_kafka", description="Source of the analysis request")
    query: str = Field(..., description="Analysis query")
    ticker: str = Field(..., description="Stock ticker")
    
    # Trigger signal from indicators pipeline
    trigger_signal: Dict[str, Any] = Field(default_factory=dict, description="Original trade signal")
    
    # Agent outputs
    news_output: Optional[Dict[str, Any]] = Field(default=None)
    twitter_output: Optional[Dict[str, Any]] = Field(default=None)
    montecarlo_output: Optional[Dict[str, Any]] = Field(default=None)
    fundamental_output: Optional[Dict[str, Any]] = Field(default=None)
    
    # Final response
    final_response: str = Field(..., description="Aggregated analysis response")
    agent_contributions: List[str] = Field(default_factory=list)
    
    # Publishing decision
    should_publish: bool = Field(default=True, description="Whether this should be published")
    conflict_reason: Optional[str] = Field(default=None, description="Reason if not publishing")
    
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    class Config:
        extra = "allow"

