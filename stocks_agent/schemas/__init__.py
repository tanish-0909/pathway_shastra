"""
Input and output schemas for StocksAgent agents.
"""

from .inputs import (
    NewsInput,
    TwitterInput,
    MontecarloInput,
    TechnicalInput,
    FundamentalInput,
)
from .outputs import (
    NewsOutput,
    TwitterOutput,
    MontecarloOutput,
    TechnicalOutput,
    FundamentalOutput,
)
from .kafka_schemas import (
    TradeSignal,
    StockAnalysis,
)

__all__ = [
    "NewsInput",
    "TwitterInput",
    "MontecarloInput",
    "TechnicalInput",
    "FundamentalInput",
    "NewsOutput",
    "TwitterOutput",
    "MontecarloOutput",
    "TechnicalOutput",
    "FundamentalOutput",
    "TradeSignal",
    "StockAnalysis",
]

