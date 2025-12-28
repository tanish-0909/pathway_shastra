"""
Pathway Log Return Service.

Computes log returns using Pathway's streaming pipeline with sliding windows.
"""

import os
import logging
from pathlib import Path
from typing import Optional, List, Tuple
from datetime import timedelta

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

try:
    import pathway as pw
    PATHWAY_AVAILABLE = True
except ImportError:
    pw = None
    PATHWAY_AVAILABLE = False

if PATHWAY_AVAILABLE:
    class InputSchema(pw.Schema):
        close: float
        date: str

    class LogReturnAccumulator(pw.BaseCustomAccumulator):
        """Accumulates (timestamp, price) pairs for log return calculation."""
        
        def __init__(self, price_data: List[Tuple]):
            self.price_data = list(price_data)
        
        @classmethod
        def from_row(cls, row: Tuple) -> 'LogReturnAccumulator':
            timestamp, price = row
            return cls([(timestamp, price)])
        
        def update(self, other: 'LogReturnAccumulator') -> None:
            self.price_data.extend(other.price_data)
        
        def retract(self, other: 'LogReturnAccumulator') -> None:
            for item in other.price_data:
                try:
                    self.price_data.remove(item)
                except ValueError:
                    pass
        
        def compute_result(self) -> float:
            if len(self.price_data) < 2:
                return 0.0
            
            try:
                sorted_data = sorted(self.price_data, key=lambda x: x[0])
                first_price = sorted_data[0][1]
                last_price = sorted_data[-1][1]
                
                if first_price <= 0 or last_price <= 0:
                    return 0.0
                
                return float(np.log(last_price / first_price))
            except Exception:
                return 0.0


class PathwayServiceError(Exception):
    """Exception for Pathway service failures."""
    pass


class PathwayLogReturnService:
    """
    Service for computing log returns using Pathway streaming pipeline.
    """
    
    def __init__(
        self,
        window_duration_minutes: int = 10,
        hop_duration_minutes: int = 5
    ):
        self.window_duration = window_duration_minutes
        self.hop_duration = hop_duration_minutes
        self._pathway_available = PATHWAY_AVAILABLE
    
    def compute_log_returns_pathway(self, input_csv_path: str) -> str:
        """
        Compute log returns using Pathway pipeline.
        """
        if not self._pathway_available:
            return self.compute_log_returns_fallback(input_csv_path)
        
        input_path = Path(input_csv_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        logger.info(f"Initializing Pathway pipeline for {input_path}...")
        
        data = pw.io.csv.read(
            str(input_path),
            schema=InputSchema,
            mode="static"
        )
        
        data = data.with_columns(
            timestamp=data.date.dt.strptime(fmt="%Y-%m-%d %H:%M:%S%z")
        )
        
        # Create reducer
        log_return_reducer = pw.reducers.udf_reducer(LogReturnAccumulator)
        
        logger.info(
            f"Applying sliding window: Duration={self.window_duration}m, "
            f"Hop={self.hop_duration}m"
        )
        
        result_table = data.windowby(
            data.timestamp,
            window=pw.temporal.sliding(
                duration=timedelta(minutes=self.window_duration),
                hop=timedelta(minutes=self.hop_duration)
            ),
            behavior=pw.temporal.exactly_once_behavior()
        ).reduce(
            window_end=pw.this._pw_window_end,
            date=pw.reducers.max(pw.this.date),
            close=pw.reducers.max((pw.this.date, pw.this.close)),
            log_ret=log_return_reducer(pw.this.timestamp, pw.this.close),
        )
        
        output_path = input_path.with_name(
            f"{input_path.stem}{input_path.suffix}"
        )
        
        logger.info(f"Writing results to: {output_path}")
        pw.io.csv.write(result_table, str(output_path))
        
        logger.info("Starting Pathway engine...")
        try:
            pw.run()
            logger.info("Pipeline completed successfully.")
            return str(output_path)
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise PathwayServiceError(f"Pathway pipeline failed: {e}")
    
    def compute_log_returns_fallback(self, input_csv_path: str) -> str:
        """
        Fallback method to compute log returns without Pathway.
        """
        input_path = Path(input_csv_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        logger.info(f"Computing log returns (fallback mode) for {input_path}...")
        
        df = pd.read_csv(input_path)
        
        if 'close' not in df.columns:
            raise ValueError(f"CSV missing 'close' column. Available: {df.columns.tolist()}")
        
        if 'date' in df.columns:
            df = df.sort_values('date').reset_index(drop=True)
        
        # Calculate log returns
        df['log_ret'] = np.log(df['close'] / df['close'].shift(1))
        
        # Drop first row (NaN from shift)
        df = df.dropna(subset=['log_ret'])
        
        output_path = input_path.with_name(
            f"{input_path.stem}_processed{input_path.suffix}"
        )
        df.to_csv(output_path, index=False)
        
        logger.info(f"Saved {len(df)} rows with log returns to {output_path}")
        return str(output_path)
    
    def compute_log_returns(self, input_csv_path: str) -> str:
        """
        Compute log returns using best available method.
        """
        if self._pathway_available:
            try:
                return self.compute_log_returns_pathway(input_csv_path)
            except Exception as e:
                logger.warning(f"Pathway failed, falling back: {e}")
                return self.compute_log_returns_fallback(input_csv_path)
        else:
            return self.compute_log_returns_fallback(input_csv_path)