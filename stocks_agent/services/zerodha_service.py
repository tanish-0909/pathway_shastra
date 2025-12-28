import os
import json
import logging
import datetime
import re
import sys
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
from functools import lru_cache
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
import pandas as pd
from kiteconnect import KiteConnect, exceptions as kite_exceptions


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

SCRIPT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = SCRIPT_DIR / "data"
print(f"Data directory set to: {DATA_DIR}", f"script dir is here: {SCRIPT_DIR}")
logger = logging.getLogger(__name__)


class DataPipelineError(Exception):
    """Base exception for data pipeline failures."""
    pass

class ConfigurationError(DataPipelineError):
    """Raised when configuration or environment variables are missing."""
    pass


class ZerodhaDataManager:
    """
    Manages authentication and data retrieval from the Zerodha Kite Connect API.
    """

    def __init__(self, universe_path: str = None, instruments_path: str = None):
        self._load_credentials()
        self.kite = self._initialize_client()
        # Use provided paths or default to DATA_DIR
        if universe_path is None:
            universe_path = DATA_DIR / "UNIVERSE.json"
        if instruments_path is None:
            instruments_path = DATA_DIR / "Zerodha_Instrument_Tokens.csv"
        self.instruments_path = Path(instruments_path)
        self.universe = self._load_universe(universe_path)
        self.instrument_df = None  
        
    def _load_credentials(self):
        """Validates existence of required environment variables."""
        load_dotenv()
        self.api_key = os.getenv("ZERODHA_API_KEY")
        self.access_token = os.getenv("ZERODHA_ACCESS_TOKEN")
        
        if not self.api_key or not self.access_token:
            raise ConfigurationError("Missing ZERODHA_API_KEY or ZERODHA_ACCESS_TOKEN in environment variables.")

    def _initialize_client(self) -> KiteConnect:
        """Initializes the KiteConnect client."""
        try:
            kite = KiteConnect(api_key=self.api_key)
            kite.set_access_token(self.access_token)
            return kite
        except Exception as e:
            logger.error(f"Failed to initialize KiteConnect: {e}")
            raise DataPipelineError(f"Client initialization failed: {e}")

    def _load_universe(self, path: str) -> Dict[str, int]:
        """Loads the instrument universe mapping once to memory."""
        file_path = Path(path)
        if not file_path.exists():
            raise ConfigurationError(f"Universe file not found at: {path}")
        
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in universe file: {e}")

    @lru_cache(maxsize=100)
    def _get_instrument_token(self, ticker: str) -> int:
        """
        Retrieves instrument token with LRU cache.
        Loads CSV only once into memory (lazy loading) and uses Regex for cleaner matching.
        """
        if ticker in self.universe.keys():
            return self.universe[ticker]

        # 1. Optimized DF Loading: Load once and cache in memory
        if self.instrument_df is None:
            if not Path(self.instruments_path).exists():
                raise ConfigurationError(f"Instrument token file not found: {self.instruments_path}")
            self.instrument_df = pd.read_csv(self.instruments_path)
            # Ensure we are working with string types for matching
            self.instrument_df['tradingsymbol'] = self.instrument_df['tradingsymbol'].astype(str)

        df = self.instrument_df
        
        # 2. Optimized Ticker Conversion: Use Regex for cleaner suffix removal
        ticker_upper = ticker.strip().upper()
        
        # Removes .NS, .BO, and company suffixes (LTD, LIMITED) found at the end of the string
        ticker_clean = re.sub(r'(\.NS|\.BO|\sLTD\.?|\sLIMITED)$', '', ticker_upper).strip()
        ticker_no_spaces = ticker_clean.replace(' ', '')
        
        # Try exact match on tradingsymbol
        mask = df['tradingsymbol'].str.upper() == ticker_clean
        if mask.any():
            return int(df.loc[mask, 'instrument_token'].iloc[0])
        
        # Try without spaces
        mask = df['tradingsymbol'].str.upper() == ticker_no_spaces
        print(f"Trying no spaces match for {ticker_no_spaces}")
        if mask.any():
            token = int(df.loc[mask, 'instrument_token'].iloc[0])
            print(f"Found token {token} for {ticker_no_spaces}")
            return token
        
        # Try first word
        words = ticker_clean.split()
        if words:
            first_word = words[0]
            mask = df['tradingsymbol'].str.upper() == first_word
            if mask.any():
                return int(df.loc[mask, 'instrument_token'].iloc[0])
        
        # Try partial match on name
        mask = df['name'].str.upper().str.contains(ticker_clean, regex=False, na=False)
        if mask.any():
            return int(df.loc[mask, 'instrument_token'].iloc[0])
        
        raise ValueError(f"Instrument token not found for: {ticker}")


    def _sanitize_filename(self, ticker: str) -> str:
        """Creates a clean filename from a ticker symbol using Regex."""

        clean_name = re.sub(r'[^a-zA-Z0-9]', '', ticker)
        return clean_name

    def fetch_data(self, ticker: str, start_date: datetime.datetime, end_date: datetime.datetime, interval: str) -> List[Dict[str, Any]]:
        """
        Core logic to fetch data. Returns raw list of dictionaries.
        """
        token = self._get_instrument_token(ticker)
        
        try:
            logger.debug(f"Fetching {interval} data for {ticker} ({token}) from {start_date} to {end_date}")
            data = self.kite.historical_data(
                instrument_token=token,
                from_date=start_date,
                to_date=end_date,
                interval=interval
            )
            return data
            
        except kite_exceptions.InputException as e:
            logger.error(f"Input error for {ticker}: {e}")
            raise DataPipelineError(f"Invalid input params: {e}")
        except kite_exceptions.NetworkException as e:
            logger.error(f"Network error fetching {ticker}: {e}")
            raise DataPipelineError("Network connection to Zerodha failed.")
        except Exception as e:
            logger.error(f"Unexpected error fetching {ticker}: {e}")
            raise

    def get_recent_data(self, ticker: str, duration_minutes: int = 5) -> List[Dict[str, Any]]:
        """
        Fetches the most recent X minutes of data.
        """
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(minutes=duration_minutes)
        
        data = self.fetch_data(ticker, start_date, end_date, interval="5minute")
        
        if not data:
            logger.warning(f"No data returned for {ticker} in the last {duration_minutes} minutes.")
            return []
            
        return data

    def download_historical_csv(self, ticker: str, start_date: datetime.date, end_date: datetime.date, interval: str = "5minute", output_dir: str = "historical_data") -> Optional[str]:
        """
        Fetches data and saves to CSV. Returns the file path on success.
        """
        try:
            data = self.fetch_data(ticker, start_date, end_date, interval)
            
            if not data:
                logger.warning(f"No data found for {ticker} in specified range.")
                return None

            df = pd.DataFrame(data)
            
            clean_ticker = self._sanitize_filename(ticker)
            save_dir = Path(output_dir)
            save_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{clean_ticker}_{interval}.csv"
            file_path = save_dir / filename
            
            df.to_csv(file_path, index=False)
            logger.info(f"Saved {len(df)} rows to {file_path}")
            return str(file_path)

        except DataPipelineError:
            return None


if __name__ == "__main__":
    # Ensure you have set these env vars before running:
    # export ZERODHA_API_KEY="your_key"
    # export ZERODHA_ACCESS_TOKEN="your_token"
    
    try:
        # Initialize Manager
        dm = ZerodhaDataManager()
        
        # Define Date Range
        today = datetime.date.today()
        start_hist = today - datetime.timedelta(days=100)
        
        # 1. Fetch and Save Historical CSV
        logger.info("Starting historical download...")
        
        csv_path = dm.download_historical_csv(
            ticker="INDIGO", 
            start_date=start_hist, 
            end_date=today, 
            interval="5minute"
        )
        
        if csv_path:
            print(f"File ready at: {csv_path}")

        # 2. Fetch Live/Recent Data (In-memory)
        # logger.info("Fetching recent data...")
        
        # live_data = dm.get_recent_data("Reliance Industries Ltd", duration_minutes=5)
        
        # if live_data:
        #     print(f"Received {len(live_data)} recent data points.")
        #     print(f"Latest Close: {live_data[-1].get('close')}")
        # else:
        #     print("No recent data available.")

    except ConfigurationError as e:
        logger.critical(f"Configuration Failed: {e}")
    except DataPipelineError as e:
        logger.error(f"Pipeline Failed: {e}")
    except Exception as e:
        logger.exception(f"Unhandled system crash: {e}")