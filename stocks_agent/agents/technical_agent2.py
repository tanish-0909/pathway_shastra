"""
Technical Analysis Agent - Computes technical indicators and generates signals.
Refactored: Robust Date Parsing with Safe Defaults.
"""


import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Union, Optional
from pydantic import BaseModel
import json


import pandas as pd


# Path setup
current_file = Path(os.path.abspath(__file__))
project_root = current_file.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


from agents.base import BaseAgent
from schemas.inputs import TechnicalInput
from schemas.outputs import TechnicalOutput
from state import StockAgentState
from agents.accessories.technical import TechnicalIndicators
from services.zerodha_service import ZerodhaDataManager


logger = logging.getLogger(__name__)



class TechnicalAgent(BaseAgent):
    """
    Agent that performs technical analysis on a stock.
    Calculates indicators based on a specific time range (start/end) 
    and interval provided in the input.
    """
    
    name = "technical_agent"
    description = "Performs technical analysis and generates trading signals on custom timeframes"
    input_schema = TechnicalInput
    output_schema = TechnicalOutput
    
    # Safe defaults
    DEFAULT_INTERVAL = "15minute"
    DEFAULT_LOOKBACK_DAYS = 10
    
    def __init__(self):
        super().__init__()
        self.indicators = TechnicalIndicators()
        
        # Data paths
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.historical_dir = Path(__file__).parent.parent.parent / "historical_data"
        self.historical_dir.mkdir(parents=True, exist_ok=True)
    
    def _collect_stock_data(self, ticker: str, start_date: datetime, end_date: datetime, interval: str) -> str:
        """
        Collect historical stock data from Zerodha for a specific range and interval.
        """
        try:
            dm = ZerodhaDataManager()
            
            logger.info(f"Downloading data for {ticker} | Interval: {interval} | {start_date} to {end_date}")
            
            csv_path = dm.download_historical_csv(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                interval=interval,
                output_dir=str(self.historical_dir)
            )
            
            if not csv_path:
                raise ValueError(f"Failed to download data for {ticker}")
            
            logger.info(f"Data downloaded: {csv_path}")
            return csv_path
        
        except Exception as e:
            logger.error(f"Error collecting stock data: {e}")
            raise
    
    def _calculate_and_save_indicators(self, csv_path: str, ticker: str) -> pd.DataFrame:
        """Calculate indicators and save to CSV."""
        df = pd.read_csv(csv_path)
        
        if df.empty:
            raise ValueError(f"Downloaded CSV for {ticker} is empty.")


        # Calculate all indicators using core module
        df = self.indicators.calculate_all_indicators(df)
        
        # Save output
        clean_ticker = ticker.replace(' ', '_')
        output_path = self.historical_dir / f"TA_{clean_ticker}_indicators.csv"
        df.to_csv(output_path, index=False)
        
        logger.info(f"Indicators saved to {output_path}")
        return df
    
    def _parse_date(self, date_input: Any, default: datetime) -> datetime:
        """
        Helper to safely parse dates that might be Strings, Datetimes, or None.
        """
        if date_input is None:
            return default
            
        if isinstance(date_input, datetime):
            return date_input
            
        if isinstance(date_input, str):
            try:
                # Try ISO format
                return datetime.fromisoformat(date_input)
            except ValueError:
                logger.warning(f"Could not parse date string '{date_input}', using default.")
                return default
                
        return default
    
    def _get_safe_dates_and_interval(self, data_dict: Dict[str, Any]) -> tuple[datetime, datetime, str]:
        """
        Extract and validate dates and interval from input with safe fallbacks.
        
        Returns:
            tuple: (start_date, end_date, interval)
        """
        try:
            # Step 1: Parse interval with fallback
            interval = data_dict.get("interval", self.DEFAULT_INTERVAL)
            if not interval or not isinstance(interval, str):
                logger.warning(f"Invalid interval '{interval}', using default: {self.DEFAULT_INTERVAL}")
                interval = self.DEFAULT_INTERVAL
            
            # Step 2: Parse end_date with fallback
            try:
                raw_end = data_dict.get("end_date")
                end_date = self._parse_date(raw_end, default=datetime.now())
            except Exception as e:
                logger.warning(f"Error parsing end_date: {e}. Using now().")
                end_date = datetime.now()
            
            # Step 3: Parse start_date with fallback
            try:
                raw_start = data_dict.get("start_date")
                default_start = end_date - timedelta(days=self.DEFAULT_LOOKBACK_DAYS)
                start_date = self._parse_date(raw_start, default=default_start)
            except Exception as e:
                logger.warning(f"Error parsing start_date: {e}. Using {self.DEFAULT_LOOKBACK_DAYS} days ago.")
                start_date = end_date - timedelta(days=self.DEFAULT_LOOKBACK_DAYS)
            
            # Step 4: Validate that start < end
            if start_date >= end_date:
                logger.error(f"Invalid date range: start ({start_date}) >= end ({end_date}). Resetting to defaults.")
                end_date = datetime.now()
                start_date = end_date - timedelta(days=self.DEFAULT_LOOKBACK_DAYS)
                interval = self.DEFAULT_INTERVAL
            
            return start_date, end_date, interval
            
        except Exception as e:
            # Nuclear fallback: if anything goes wrong, use safe defaults
            logger.error(f"Critical error in date/interval parsing: {e}. Using safe defaults.")
            end_date = datetime.now()
            start_date = end_date - timedelta(days=self.DEFAULT_LOOKBACK_DAYS)
            interval = self.DEFAULT_INTERVAL
            return start_date, end_date, interval


    def run(self, input_data: Union[Dict[str, Any], BaseModel], state: StockAgentState) -> Dict[str, Any]:
        """
        Main entry point for the agent.
        """
        # Handle input validation
        if isinstance(input_data, BaseModel):
            data_dict = input_data.model_dump()
        else:
            data_dict = input_data


        ticker = data_dict.get("ticker", "")
        
        # Safe extraction with fallbacks
        start_date, end_date, interval = self._get_safe_dates_and_interval(data_dict)


        logger.debug(f"=== TECHNICAL AGENT DATE DEBUG ===")
        logger.debug(f"Raw Input: {data_dict}")
        logger.info(f"Final Timeframe: Ticker={ticker}, Interval={interval}")
        logger.info(f"Final Timeframe: Start={start_date}, End={end_date}")
        logger.debug(f"=================================\n")


        if not ticker:
            logger.warning("Technical Agent: No ticker provided")
            return self._error_response("No ticker provided", "UNKNOWN")
        
        logger.info(f"Technical Agent: Processing {ticker}")
        
        try:
            # STEP 1: Collect Data
            csv_path = self._collect_stock_data(ticker, start_date, end_date, interval)
            
            # STEP 2: Calculate Indicators
            df = self._calculate_and_save_indicators(csv_path, ticker)
            data_source = "calculated_live"
            
            # STEP 3: Determine Signal
            signal, reason, strength, _ = self.indicators.determine_signal(df)
            
            # Format date for JSON output
            if 'date' in df.columns:
                if not pd.api.types.is_datetime64_any_dtype(df['date']):
                     df['date'] = pd.to_datetime(df['date'], utc=True)
                
                df['date'] = df['date'].dt.tz_convert('Asia/Kolkata')            
                df['date'] = df['date'].dt.strftime('%Y-%m-%d %H:%M:%S %z')
                df_indexed = df.set_index('date', drop=False)
            else:
                df_indexed = df


            json_output = df_indexed.to_json(orient='index', indent=4)
            
            clean_ticker = ticker.replace(' ', '_')
            output_path_json = str(self.historical_dir / f"TA_{clean_ticker}_indicators.json")


            try:
                with open(output_path_json, 'w') as f:
                    f.write(json_output)
            except Exception as e:
                logger.error(f"Error saving JSON file: {e}")


            reason = f"[{interval.upper()}] {reason}"
            
            # STEP 4: Create Output
            result = TechnicalOutput(
                status="success",
                ticker=ticker,
                signal=signal,
                strength=float(strength),
                reason=reason,
                json_data=json.loads(json_output),
                timestamp=datetime.now().isoformat()
            )
            
            state_update = {
                "technical_output": result.model_dump(),
                "agent_contributions": [self.name],
                "data_source": data_source
            }
            
            logger.info(f"Technical Agent: Signal {signal} for {ticker} ({interval})")
            
            return state_update
        
        except Exception as e:
            logger.error(f"Technical Agent failed for {ticker}: {e}", exc_info=True)
            return self._error_response(str(e), ticker)
    
    def _error_response(self, error_msg: str, ticker: str) -> Dict[str, Any]:
        result = TechnicalOutput(
            status="error",
            ticker=ticker,
            signal="HOLD",
            strength=0.0,
            reason=error_msg,
            json_data={},
            timestamp=datetime.now().isoformat()
        )
        return {
            "technical_output": result.model_dump(),
            "agent_contributions": [f"{self.name} (Failed)"],
            "errors": [f"Technical Agent Error: {error_msg}"]
        }


if __name__ == "__main__":
    agent = TechnicalAgent()
    
    # Test Case 1: String Input
    print("\n━━━ Test 1: String Input ━━━")
    test_input_str = {
        "ticker": "INDIGO",
        "start_date": (datetime.now() - timedelta(days=5)).isoformat(),
        "end_date": datetime.now().isoformat(),
        "interval": "day"
    }
    agent.run(test_input_str, {})
    
    # Test Case 2: Datetime Input (Simulating Pydantic conversion)
    print("\n━━━ Test 2: Datetime Object Input ━━━")
    test_input_obj = {
        "ticker": "INDIGO",
        "start_date": datetime.now() - timedelta(days=5),
        "end_date": datetime.now(),
        "interval": "day"
    }
    agent.run(test_input_obj, {})
    
    # Test Case 3: Invalid/Missing dates and interval
    print("\n━━━ Test 3: Invalid Input (Should Use Defaults) ━━━")
    test_input_invalid = {
        "ticker": "INDIGO",
        "start_date": "invalid-date",
        "end_date": None,
        "interval": None
    }
    agent.run(test_input_invalid, {})
    
    # Test Case 4: Start > End (Should Reset)
    print("\n━━━ Test 4: Start > End (Should Reset) ━━━")
    test_input_reversed = {
        "ticker": "INDIGO",
        "start_date": datetime.now(),
        "end_date": datetime.now() - timedelta(days=5),
        "interval": "5minute"
    }
    agent.run(test_input_reversed, {})
