"""
Montecarlo Agent - Runs Monte Carlo simulations for stock price prediction.

Supports one mode:
- real: Uses Zerodha API + Pathway pipeline for actual simulations
"""

import sys
import os
import logging
import datetime
from typing import Dict, Any
from pathlib import Path

current_file = Path(os.path.abspath(__file__))
parent_dir = current_file.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from agents.base import BaseAgent
from schemas.inputs import MontecarloInput
from schemas.outputs import MontecarloOutput
from state import StockAgentState as AgentState
from pathlib import Path
from services.zerodha_service import ZerodhaDataManager
from services.pw_logret_service_mc import PathwayLogReturnService
from agents.accessories.montecarlo import MonteCarloSimulator


logger = logging.getLogger(__name__)


class MontecarloAgent(BaseAgent):
    """
    Agent that runs Monte Carlo simulations for stock price prediction.
    
    Input: ticker, days_history, simulation_days, num_simulations, mode
    Output: results (dict with simulation metrics)
    """
    
    name = "montecarlo_agent"
    description = "Runs Monte Carlo simulations for price prediction"
    input_schema = MontecarloInput
    output_schema = MontecarloOutput
    
    def run(self, input_data: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        """
        Execute Monte Carlo simulation based on mode.
        
        Args:
            input_data: Validated input parameters
            state: Current agent state
            
        Returns:
            Dictionary with montecarlo_output and agent_contributions
        """
        mode = input_data.get("mode", "real")
        
        if mode == "real":
            return self._run_real_simulation(input_data)
        else:
            return {"error":'Error calling Monte Carlo'}
    
    def _run_real_simulation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run actual Monte Carlo simulation using Zerodha data and Pathway pipeline.
        
        Flow:
        1. Download historical data from Zerodha
        2. Compute log returns using Pathway (or fallback)
        3. Run Monte Carlo bootstrap simulation
        4. Return statistical results
        """
        ticker = input_data["ticker"]
        days_history = input_data.get("days_history", 100)
        simulation_days = input_data.get("simulation_days", 15)
        num_simulations = input_data.get("num_simulations", 1_000_000)
        
        logger.info(f"[REAL] Running Monte Carlo simulation for {ticker}")
        logger.info(f"  History: {days_history} days")
        logger.info(f"  Simulation: {simulation_days} days, {num_simulations} paths")
        
        try:
            
            # Get data directory path
            data_dir = Path(__file__).parent.parent.parent / "data"
            universe_path = str(data_dir / "UNIVERSE.json")
            instruments_path = str(data_dir / "Zerodha_Intrument_Tokens.csv")
            
            # Step 1: Download historical data
            logger.info("Step 1: Downloading historical data from Zerodha...")
            zerodha = ZerodhaDataManager(
                universe_path=universe_path,
                instruments_path=instruments_path
            )
            
            today = datetime.date.today()
            start_date = today - datetime.timedelta(days=days_history)
            
            historical_csv = zerodha.download_historical_csv(
                ticker=ticker,
                start_date=start_date,
                end_date=today,
                interval="5minute"
            )
            
            if not historical_csv:
                raise ValueError(f"Failed to download data for ticker: {ticker}")
            
            logger.info(f"Historical data saved to: {historical_csv}")
            
            # Step 2: Compute log returns
            logger.info("Step 2: Computing log returns...")
            pathway_service = PathwayLogReturnService()
            log_returns_csv = pathway_service.compute_log_returns(historical_csv)
            
            logger.info(f"Log returns saved to: {log_returns_csv}")
            
            # Step 3: Run Monte Carlo simulation
            logger.info("Step 3: Running Monte Carlo simulation...")
            simulator = MonteCarloSimulator(
                num_simulations=num_simulations,
                simulation_days=simulation_days
            )
            
            results = simulator.evaluate(log_returns_csv)
            
            # Add metadata
            results["ticker"] = ticker
            results["Analysis Date"] = today.isoformat()
            results["History Days"] = days_history
            results["mode"] = "real"
            
            logger.info("Monte Carlo simulation complete!")
            logger.info(f"  Mean Return: {results['Mean Return']:.2f}%")
            logger.info(f"  Prob Loss: {results['Probability of Loss']:.1%}")
            
            output = MontecarloOutput(results=results)
            
            return {
                "montecarlo_output": output.model_dump(),
                "agent_contributions": [self.name]
            }
            
        except ImportError as e:
            logger.error(f"Missing dependency for real mode: {e}")
            return {
                "montecarlo_output": {"results": {"error": f"Missing dependency: {e}"}},
                "agent_contributions": [f"{self.name} (Failed)"],
                "errors": [str(e)]
            }
            
        except Exception as e:
            logger.error(f"Real simulation failed: {e}")
            return {
                "montecarlo_output": {"results": {"error": f"Missing dependency: {e}"}},
                "agent_contributions": [f"{self.name} (Failed)"],
                "errors": [str(e)]
            }
