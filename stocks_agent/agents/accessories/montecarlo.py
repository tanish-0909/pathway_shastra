"""
Core Monte Carlo Simulation Logic.

This module contains pure simulation functions with no external API dependencies.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

import numpy as np
import pandas as pd


logger = logging.getLogger(__name__)


class MonteCarloSimulator:
    """
    Monte Carlo simulation engine for stock price prediction.
    
    Uses bootstrap sampling of historical log returns to simulate
    future price paths and calculate risk/return metrics.
    """
    
    def __init__(
        self,
        num_simulations: int = 1_000_000,
        simulation_days: int = 15
    ):
        """
        Initialize the simulator.
        
        Args:
            num_simulations: Number of Monte Carlo paths to simulate
            simulation_days: Number of days to simulate forward
        """
        self.num_simulations = num_simulations
        self.simulation_days = simulation_days
    
    @staticmethod
    def parse_close_price(close_value) -> float:
        """
        Parse close price from various formats including Pathway output.
        
        Args:
            close_value: Close price as JSON array string, tuple, or number
            
        Returns:
            float: Parsed close price
        """
        import json
        
        # If already a number, return it
        if isinstance(close_value, (int, float)):
            return float(close_value)
        
        # Try parsing as JSON array ["date", price]
        try:
            parsed = json.loads(str(close_value))
            if isinstance(parsed, list) and len(parsed) >= 2:
                return float(parsed[1])
            return float(parsed)
        except (json.JSONDecodeError, TypeError, IndexError):
            pass
        
        # Try parsing as tuple string
        try:
            if isinstance(close_value, str) and close_value.startswith('('):
                import ast
                parsed = ast.literal_eval(close_value)
                if isinstance(parsed, tuple) and len(parsed) >= 2:
                    return float(parsed[1])
        except (ValueError, SyntaxError):
            pass
        
        return float(close_value)
    
    def get_initial_price_from_csv(self, csv_path: str) -> float:
        """
        Extract initial (latest) close price from CSV file.
        
        Args:
            csv_path: Path to CSV file with 'close' column
            
        Returns:
            float: Latest close price from the dataset
            
        Raises:
            FileNotFoundError: If CSV doesn't exist
            ValueError: If CSV is empty or missing 'close' column
        """
        if not Path(csv_path).exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        df = pd.read_csv(csv_path)
        
        if df.empty:
            raise ValueError(f"CSV file is empty: {csv_path}")
        
        if 'close' not in df.columns:
            raise ValueError(f"CSV missing 'close' column. Available: {df.columns.tolist()}")
        
        # Sort by date to get chronological order
        if 'date' in df.columns:
            df = df.sort_values(by="date")
        
        # Get last non-null close value
        close_values = df['close'].dropna()
        
        if len(close_values) == 0:
            raise ValueError("No valid close prices found in CSV")
        
        # Parse the last close value (handles various formats)
        last_close_raw = close_values.iloc[-1]
        initial_price = self.parse_close_price(last_close_raw)
        
        logger.info(f"Extracted initial price: {initial_price}")
        return initial_price
    
    def bootstrap_simulation(
        self,
        log_returns: np.ndarray,
        initial_price: float
    ) -> np.ndarray:
        """
        Perform Monte Carlo bootstrap simulation on log returns.
        
        Args:
            log_returns: Array of historical log returns
            initial_price: Starting price for simulation
            
        Returns:
            np.ndarray: Array of total returns (percentage) for each simulation
            
        Raises:
            ValueError: If inputs are invalid
        """
        if len(log_returns) == 0:
            raise ValueError("log_returns array is empty")
        
        if initial_price <= 0:
            raise ValueError(f"initial_price must be positive, got {initial_price}")
        
        logger.info(
            f"Running Monte Carlo: {self.num_simulations} simulations "
            f"over {self.simulation_days} days"
        )
        
        # Bootstrap sample returns with replacement
        sampled_returns = np.random.choice(
            log_returns,
            size=(self.simulation_days, self.num_simulations),
            replace=True
        )
        
        # Calculate cumulative price paths using log returns
        price_paths = initial_price * np.exp(np.cumsum(sampled_returns, axis=0))
        
        # Extract final prices (last row)
        final_prices = price_paths[-1, :]
        
        # Calculate total returns as percentages
        total_returns = ((final_prices - initial_price) / initial_price) * 100
        
        return total_returns
    
    def evaluate(
        self,
        csv_path: str,
        initial_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Run full Monte Carlo evaluation from a CSV with log returns.
        
        Args:
            csv_path: Path to CSV file with 'log_ret' column
            initial_price: Starting price (if None, extracted from CSV 'close' column)
            
        Returns:
            dict: Dictionary containing simulation results and statistics
        """
        logger.info(f"Starting Monte Carlo evaluation on: {csv_path}")
        
        if not Path(csv_path).exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        # Load data
        df = pd.read_csv(csv_path)
        
        if df.empty:
            raise ValueError(f"CSV file is empty: {csv_path}")
        
        if 'log_ret' not in df.columns:
            raise ValueError(
                f"CSV missing 'log_ret' column. Available: {df.columns.tolist()}"
            )
        
        # Get log returns
        log_returns = df['log_ret'].dropna().values
        
        if len(log_returns) < 2:
            raise ValueError(f"Insufficient log returns data: {len(log_returns)} rows")
        
        # Get initial price
        if initial_price is None:
            initial_price = self.get_initial_price_from_csv(csv_path)
        
        if initial_price <= 0:
            raise ValueError(f"Invalid initial price: {initial_price}")
        
        # Calculate input statistics
        mean_log_return = float(np.mean(log_returns))
        std_log_return = float(np.std(log_returns, ddof=1))
        
        logger.info(f"Log returns - Mean: {mean_log_return:.6f}, Std: {std_log_return:.6f}")
        
        # Run simulation
        simulation_results = self.bootstrap_simulation(log_returns, initial_price)
        
        # Calculate output statistics
        prob_loss = float(np.mean(simulation_results < 0))
        
        results = {
            "Min Return": float(np.min(simulation_results)),
            "Max Return": float(np.max(simulation_results)),
            "Mean Return": float(np.mean(simulation_results)),
            "Median Return": float(np.median(simulation_results)),
            "Std Deviation": float(np.std(simulation_results, ddof=1)),
            "Probability of Loss": prob_loss,
            "5th Percentile": float(np.percentile(simulation_results, 5)),
            "95th Percentile": float(np.percentile(simulation_results, 95)),
            "10th Percentile": float(np.percentile(simulation_results, 10)),
            "90th Percentile": float(np.percentile(simulation_results, 90)),
            "Mean Log Return": mean_log_return,
            "Std Log Return": std_log_return,
            "Initial Price": initial_price,
            "Num Simulations": self.num_simulations,
            "Num Days": self.simulation_days,
        }
        
        logger.info(f"Monte Carlo evaluation complete. Prob Loss: {prob_loss:.2%}")
        return results
    
    def evaluate_from_prices(
        self,
        prices: np.ndarray,
        initial_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo evaluation directly from price array.
        
        Args:
            prices: Array of historical prices
            initial_price: Starting price (if None, uses last price in array)
            
        Returns:
            dict: Dictionary containing simulation results
        """
        if len(prices) < 2:
            raise ValueError(f"Need at least 2 prices, got {len(prices)}")
        
        # Calculate log returns
        log_returns = np.diff(np.log(prices))
        
        # Use last price as initial if not provided
        if initial_price is None:
            initial_price = float(prices[-1])
        
        # Calculate statistics
        mean_log_return = float(np.mean(log_returns))
        std_log_return = float(np.std(log_returns, ddof=1))
        
        # Run simulation
        simulation_results = self.bootstrap_simulation(log_returns, initial_price)
        
        # Calculate statistics
        prob_loss = float(np.mean(simulation_results < 0))
        
        results = {
            "Min Return": float(np.min(simulation_results)),
            "Max Return": float(np.max(simulation_results)),
            "Mean Return": float(np.mean(simulation_results)),
            "Median Return": float(np.median(simulation_results)),
            "Std Deviation": float(np.std(simulation_results, ddof=1)),
            "Probability of Loss": prob_loss,
            "5th Percentile": float(np.percentile(simulation_results, 5)),
            "95th Percentile": float(np.percentile(simulation_results, 95)),
            "Mean Log Return": mean_log_return,
            "Std Log Return": std_log_return,
            "Initial Price": initial_price,
            "Num Simulations": self.num_simulations,
            "Num Days": self.simulation_days,
        }
        
        return results

