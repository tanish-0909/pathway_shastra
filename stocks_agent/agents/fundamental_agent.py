"""
Fundamental Analysis Agent - Analyzes company fundamentals and valuations.
"""

import sys
from pathlib import Path
from typing import Dict, Any

current_file = Path(__file__).resolve()
parent = current_file.parent.parent
sys.path.append(str(parent))

from agents.base import BaseAgent
from schemas.inputs import FundamentalInput
from schemas.outputs import FundamentalOutput
from state import StockAgentState
from agents.stocks_tools.dcf_tools import get_or_create_dcf_analysis


class FundamentalAgent(BaseAgent):
    """
    Agent that returns raw DCF/fundamental analysis text for stocks.

    Input: tickers (list)
    Output: fundamental_output
    """

    name = "fundamental_agent"
    description = "Returns raw DCF/fundamental markdown from the DCF pipeline"
    input_schema = FundamentalInput
    output_schema = FundamentalOutput

    def run(self, input_data:  Dict[str, Any], state: StockAgentState) -> Dict[str, Any]:
        tickers = input_data.get("tickers", [])

        # Call the LangChain StructuredTool correctly:
        dcf_result = get_or_create_dcf_analysis.run({
            "company_names": tickers,
            "json_path": "./data_analysis.jsonlines",
        })

        status = dcf_result.get("status")
        base_analyses = dcf_result.get("analyses", {}) or {}

        analyses: Dict[str, Any] = {}

        if status == "success" or status == "partial_success":
            # Normal / partial-success path.
            # For any ticker missing from analyses, inject a clear error message.
            for t in tickers:
                if t in base_analyses and base_analyses[t]:
                    analyses[t] = base_analyses[t]
                else:
                    analyses[t] = (
                        f"Error: No DCF analysis available for {t}. "
                        f"This may be due to an upstream data or LLM failure."
                    )
        else:
            # Hard failure from the tool (e.g., auth, config, file error).
            message = dcf_result.get("message", "Unknown DCF pipeline error")
            for t in tickers:
                analyses[t] = f"Error: DCF pipeline execution failed for {t}: {message}"

        raw = {
            "fundamental_output": analyses,
            "agent_contributions": [self.name],
        }

        validated = FundamentalOutput(**raw)
        return validated.model_dump()