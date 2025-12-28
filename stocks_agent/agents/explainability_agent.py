"""
Explainability Agent - Aggregates all agent outputs into a final response 
using an LLM for synthesis and leveraging specific tools like portfolio access.
Outputs strictly in a flat JSON format for Frontend/Consumer consumption.
"""
import os
import sys
import json
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
import copy

#   Tunable Parameters  
MODEL_NAME = "gpt-4o-mini"
TEMPERATURE = 0.1
MAX_TOOL_ITERATIONS = 5
DEFAULT_USER_ID = "user_mongo_1"

#   Logging Configuration  
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

#   Path Setup  
current_file = Path(os.path.abspath(__file__))
current_dir = current_file.parent
parent_dir = current_dir.parent

if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

load_dotenv()

USER_ID = os.getenv("USER_ID", DEFAULT_USER_ID)

#   Imports  
try:
    from state import StockAgentState
    from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, BaseMessage
    from langchain_openai import ChatOpenAI
    from agents.stocks_tools.portfolio_tool import get_portfolio_tool
    from agents.stocks_tools.data_aggregator_tool import aggregate_stock_data
except ImportError as e:
    logger.critical(f"Failed to import required modules: {e}")
    sys.exit(1)


#   1. Tool Definitions & Map  
TOOL_FUNCTIONS = {}

# Map Portfolio Tool
try:
    if hasattr(get_portfolio_tool, "func"):
        TOOL_FUNCTIONS["get_portfolio_tool"] = get_portfolio_tool.func
    else:
        TOOL_FUNCTIONS["get_portfolio_tool"] = get_portfolio_tool
except Exception as e:
    logger.error(f"Error mapping portfolio tool: {e}")

# Map Aggregator Tool
try:
    if hasattr(aggregate_stock_data, "func"):
        TOOL_FUNCTIONS["aggregate_stock_data"] = aggregate_stock_data.func
    else:
        TOOL_FUNCTIONS["aggregate_stock_data"] = aggregate_stock_data
except Exception as e:
    logger.error(f"Error mapping aggregator tool: {e}")


#   2. Explainability Agent Class  

class ExplainabilityAgent:
    """
    Agent that aggregates outputs from all other agents and generates
    a comprehensive, explainable final response using an LLM.
    Enforces a strict flat JSON Schema output.
    """
    
    name = "explainability_agent"
    description = "Aggregates agent outputs and generates final explainable JSON response"
    
    def __init__(self):
        try:
            # FIX: Removed `model_kwargs={"response_format": {"type": "json_object"}}` 
            # to avoid "ValueError: tool is not strict" when binding standard tools.
            # We will enforce JSON via prompt engineering and parsing instead.
            self.llm = ChatOpenAI(
                model=MODEL_NAME, 
                temperature=TEMPERATURE
            )
            
            # We bind tools so the LLM can query portfolio data during synthesis
            self.tools = [get_portfolio_tool] 
            self.llm_with_tools = self.llm.bind_tools(self.tools)
        except Exception as e:
            logger.critical(f"Failed to initialize ChatOpenAI: {e}")
            raise e

    def _get_current_utc_time(self) -> str:
        """Helper to get timezone-aware UTC timestamp."""
        return datetime.now(timezone.utc).isoformat()

    def _clean_json_string(self, text: str) -> str:
        """Helper to strip Markdown code blocks from LLM response."""
        text = text.strip()
        # Remove ```json ... ``` or ``` ... ```
        if text.startswith("```"):
            text = re.sub(r"^```(json)?", "", text)
            text = re.sub(r"```$", "", text)
        return text.strip()

    def _get_deterministic_data(self, state: StockAgentState) -> Dict[str, Any]:
        """
        Extracts known data from State without using LLM.
        Populates tickers, agents_invoked, and raw agent outputs.
        """
        # 1. Tickers
        tickers = state.get("ticker", [])
        if isinstance(tickers, str):
            tickers = [tickers]
        elif tickers is None:
            tickers = []
            
        # 2. Extract Raw Outputs & Identify Invoked Agents
        agents_invoked = []
        
        news_output = state.get("news_output") or {}
        if news_output: agents_invoked.append("news_agent")
            
        twitter_output = state.get("twitter_output") or {}
        if twitter_output: agents_invoked.append("twitter_agent")
            
        technical_output = state.get("technical_output") or {}
        if technical_output: 
            agents_invoked.append("technical_agent")
            
        fundamental_output = state.get("fundamental_output") or {}
        if fundamental_output: agents_invoked.append("fundamental_agent")
            
        montecarlo_output = state.get("montecarlo_output") or {}
        if montecarlo_output: agents_invoked.append("montecarlo_agent")

        return {
            "meta": {
                "type": "stock_analysis_report",
                "query": state.get("query", ""),
                "timestamp": self._get_current_utc_time()
            },
            "tickers": tickers,
            "agents_invoked": agents_invoked,
            "news_output": news_output,
            "twitter_output": twitter_output,
            "technical_output": technical_output,
            "fundamental_output": fundamental_output,
            "montecarlo_output": montecarlo_output
        }

    def _prepare_context_for_llm(self, deterministic_data: Dict[str, Any], extra_context: Dict[str, Any] = None) -> str:
        """
        Prepares a text summary of the available data for the LLM to analyze.
        """
        copy_deterministic_data = copy.deepcopy(deterministic_data)
        copy_deterministic_data["technical_output"]["json_data"] = {}

        sections = [
            f"USER QUERY: {copy_deterministic_data['meta']['query']}",
            f"TICKERS: {copy_deterministic_data['tickers']}",
            "  AVAILABLE DATA  "
        ]
        
        # Add single-ticker deep dive data
        for key in ["news_output", "twitter_output", "technical_output", "fundamental_output", "montecarlo_output"]:
            if copy_deterministic_data.get(key):
                sections.append(f"== {key.upper()} ==")
                sections.append(json.dumps(copy_deterministic_data[key], indent=2, default=str))

        # Add multi-ticker aggregated data if present
        if extra_context:
            sections.append("== AGGREGATED MARKET DATA ==")
            sections.append(json.dumps(extra_context, indent=2, default=str))

        return "\n".join(sections)

    def _prepare_fallback_response(self, deterministic_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Constructs the final JSON manually when LLM is disabled.
        """
        ticker_str = ", ".join(deterministic_data["tickers"]) if deterministic_data["tickers"] else "Market"
        invoked_str = ", ".join(deterministic_data["agents_invoked"]) if deterministic_data["agents_invoked"] else "None"
        
        summary = (
            f"Automated report for {ticker_str}. "
            f"Agents executed: {invoked_str}. "
            "Please review the detailed agent outputs provided in this JSON response."
        )

        return {
            **deterministic_data,
            "portfolio_context": {
                "is_holding": False,
                "note": "Portfolio check disabled (No-LLM mode).",
                "suggested_action": "CHECK MANUALLY"
            },
            "summary": summary
        }

    def run(self, state: StockAgentState) -> Dict[str, Any]:
        """
        Generate final response.
        1. Gather deterministic data.
        2. If Multi/Zero ticker -> Run Aggregator Tool.
        3. Invoke LLM to generate 'portfolio_context' and 'summary'.
        4. Merge and return.
        """
        logger.info(f"[{self.name}] Running synthesis step...")

        #   1. Gather Deterministic Data  
        final_json = self._get_deterministic_data(state)
        
        #   2. Check Logic Path (Single vs Multi)  
        ticker_count = len(final_json["tickers"])
        is_single_ticker = (ticker_count == 1)
        
        aggregated_data = {}
        
        # If Multi/Zero: Agents didn't run via Orchestrator. Fetch aggregated data now.
        if not is_single_ticker:
            logger.info(f"[{self.name}] Multi/Zero ticker count ({ticker_count}). Invoking aggregate_stock_data.")
            try:
                aggregated_data = aggregate_stock_data.invoke({
                    "tickers": final_json["tickers"], 
                    "query": state.get("query", "")
                })
            except Exception as e:
                logger.error(f"Failed to invoke aggregate_stock_data: {e}")
                aggregated_data = {"error": str(e)}

        #   3. LLM Synthesis  
        
        context_str = self._prepare_context_for_llm(final_json, extra_context=aggregated_data)

        system_prompt = f"""
        ### ROLE
        You are the **Senior Chief Investment Strategist**.
        
        ### OBJECTIVE
        Analyze the provided data and generate a JSON response containing specific keys.
        
        ### REQUIRED ACTIONS
        1. **Check Portfolio:** You **MUST** call the tool `get_portfolio_tool` with `user_id="{USER_ID}"` to check if the user holds these assets.
        2. **Synthesize:** Provide a concise, professional summary of the situation based on the technicals, news, and fundamentals provided.
        
        ### OUTPUT FORMAT
        You must return a raw JSON object (no markdown formatting) with EXACTLY these keys:
        {{
            "portfolio_context": {{
                "is_holding": boolean,
                "current_position": "String details (e.g. '100 shares @ $150')",
                "suggested_action": "BUY | SELL | HOLD | REBALANCE"
            }},
            "summary": "A concise, high-value paragraph summarizing the signal, reasons, and risks. Do not just list data; interpret it."
        }}
        """

        try:
            messages: List[BaseMessage] = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=context_str + "\n\nProvide the required JSON output.")
            ]
            
            response = self.llm_with_tools.invoke(messages)
            
            #   Tool Execution Loop  
            iteration = 0
            while response.tool_calls and iteration < MAX_TOOL_ITERATIONS:
                logger.info(f"[{self.name}] Tool call(s) requested: {len(response.tool_calls)}")
                messages.append(response)
                tool_messages = []
                
                for tool_call in response.tool_calls:
                    tool_name = tool_call.get("name")
                    tool_args = tool_call.get("args")
                    tool_call_id = tool_call.get("id")
                    
                    try:
                        if tool_name in TOOL_FUNCTIONS:
                            logger.info(f"[{self.name}] Executing tool: {tool_name} with args: {tool_args}")
                            tool_output = TOOL_FUNCTIONS[tool_name](**tool_args)
                            tool_messages.append(ToolMessage(
                                content=str(tool_output),
                                tool_call_id=tool_call_id
                            ))
                        else:
                            tool_messages.append(ToolMessage(content="Tool not found", tool_call_id=tool_call_id))
                    except Exception as e:
                        tool_messages.append(ToolMessage(content=f"Tool Error: {e}", tool_call_id=tool_call_id))
                
                messages.extend(tool_messages)
                response = self.llm_with_tools.invoke(messages)
                iteration += 1

            #   Parse LLM JSON  
            clean_content = self._clean_json_string(response.content)
            
            try:
                llm_output = json.loads(clean_content)
            except json.JSONDecodeError:
                logger.error("Failed to parse LLM output as JSON. Returning raw content in summary.")
                llm_output = {
                    "portfolio_context": {
                        "is_holding": False,
                        "suggested_action": "MANUAL REVIEW (JSON Parse Error)"
                    },
                    "summary": response.content
                }
            
            #   5. Merge & Return  
            # Update the deterministic dict with the LLM's synthesis
            final_json.update(llm_output)
            
            return {
                "final_response": final_json
            }

        except Exception as e:
            logger.error(f"Error during LLM synthesis: {e}", exc_info=True)
            # Return what we have, plus error info
            final_json["summary"] = f"Critical Error during synthesis: {str(e)}"
            return {
                "final_response": final_json
            }

if __name__ == "__main__":
    # Mocking State for testing
    mock_state = {
        "query": "Should I sell AAPL?",
        "ticker": ["AAPL"], 
        "timeframe": "short-term",
        "technical_output": {"signal": "BUY", "strength": 8, "ticker": "AAPL"},
        "news_output": {"overall_sentiment": "Bullish", "news_output": []}
    }

    try:
        agent = ExplainabilityAgent()
        print("\n" + "="*30 + " TEST OUTPUT " + "="*30)
        res = agent.run(mock_state)
        print(json.dumps(res["final_response"], indent=2))
        
    except Exception as e:
        logger.critical(f"Main execution failed: {e}")