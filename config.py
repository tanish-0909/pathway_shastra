"""
Configuration settings for StocksAgent.

Loads settings from environment variables and provides defaults.
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

# Load .env file from project root
try:
    from dotenv import load_dotenv
    # Try ./.env first
    env_paths = [
        Path(__file__).parent / ".env",
    ]
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            break
    else:
        load_dotenv()  
except ImportError:
    pass  

# ==================== FILE PATHS ====================
INPUT_FILE = 'data/input.jsonl'
OUTPUT_FILE = 'data/output.jsonl'


# ==================== API KEYS ====================

# Stock API Key (for stock.indianapi.in)
API_KEY = os.getenv("INDIAN_MARKET_API_KEY")
# OpenRouter API Key (for LLM access)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_KEY= os.getenv("OPENAI_API_KEY")

# LLM Model for DCF Analysis (Stage 1: Financial Modeling)
DEFAULT_LLM_MODEL = "gpt-4o"

# LLM Model for Investment Decision (Stage 2: Reasoning & Decision Making)
DECISION_LLM_MODEL = "gpt-4o-mini"

# Base directory for stocksagent package
BASE_DIR = Path(__file__).parent

# Data directory
DATA_DIR = BASE_DIR / "data"


@dataclass
class ZerodhaConfig:
    """Configuration for Zerodha API integration."""
    api_key: Optional[str] = field(
        default_factory=lambda: os.environ.get("ZERODHA_API_KEY")
    )
    access_token: Optional[str] = field(
        default_factory=lambda: os.environ.get("ZERODHA_ACCESS_TOKEN")
    )
    universe_path: str = field(
        default_factory=lambda: str(DATA_DIR / "UNIVERSE.json")
    )
    instruments_path: str = field(
        default_factory=lambda: str(DATA_DIR / "Zerodha_Instrument_Tokens.csv")
    )
    output_dir: str = "historical_data"
    
    @property
    def is_configured(self) -> bool:
        """Check if Zerodha credentials are set."""
        return bool(self.api_key and self.access_token)


@dataclass
class MonteCarloConfig:
    """Default configuration for Monte Carlo simulations."""
    
    num_simulations: int = 14_000_605
    simulation_days: int = 15
    days_history: int = 100
    default_mode: str = "real"  # "mock" or "real"


@dataclass
class PathwayConfig:
    """Configuration for Pathway log return pipeline."""
    window_duration_minutes: int = 10
    hop_duration_minutes: int = 5


@dataclass
class AgentConfig:
    """Master configuration for all agents."""
    
    zerodha: ZerodhaConfig = field(default_factory=ZerodhaConfig)
    montecarlo: MonteCarloConfig = field(default_factory=MonteCarloConfig)
    pathway: PathwayConfig = field(default_factory=PathwayConfig)
    
    # Logging
    log_level: str = field(
        default_factory=lambda: os.environ.get("STOCKSAGENT_LOG_LEVEL", "INFO")
    )
    
    # Default mode for all agents
    default_mode: str = field(
        default_factory=lambda: os.environ.get("STOCKSAGENT_MODE", "mock")
    )


# Global config instance
config = AgentConfig()


def get_config() -> AgentConfig:
    """Get the global configuration instance."""
    return config


def configure_logging():
    """Configure logging based on config settings."""
    import logging
    
    log_level = getattr(logging, config.log_level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    # Set specific loggers
    logging.getLogger("stocksagent").setLevel(log_level)


def print_config_status():
    """Print current configuration status."""
    print("\n StocksAgent Configuration ")
    print(f"Mode: {config.default_mode}")
    print(f"Log Level: {config.log_level}")
    print(f"\nZerodha API:")
    print(f"  Configured: {config.zerodha.is_configured}")
    if config.zerodha.is_configured:
        print(f"  API Key: {config.zerodha.api_key[:8]}...")
    print(f"  Universe Path: {config.zerodha.universe_path}")
    print(f"  Instruments Path: {config.zerodha.instruments_path}")
    print(f"\nMonte Carlo Defaults:")
    print(f"  Simulations: {config.montecarlo.num_simulations}")
    print(f"  Simulation Days: {config.montecarlo.simulation_days}")
    print(f"  History Days: {config.montecarlo.days_history}")