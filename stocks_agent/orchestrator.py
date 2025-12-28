"""
Orchestrator - Parses user queries and determines which agents to invoke using LLM.
Optimized for Pathway Stock Agent Framework with Full Timestamp Precision.
"""

from typing import Dict, Any, List, Optional
import re
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from stocks_agent.state import StockAgentState
from stocks_agent.schemas.inputs import TechnicalInput, FundamentalInput, MontecarloInput
from stocks_agent.supporting_functions.ticker_extraction import get_bse_tickers

class AgentRoutingDecision(BaseModel):
    """
    Routing decision schema for agent execution.
    Determines which specialized Pathway agents are required to answer the user query based on strict capabilities.
    """
    tickers: List[str] = Field(
        description=(
            "A list of company names OR their stock ticker symbols as present in the user query (e.g., ['RELIANCE', 'TCS']). "
            "If the user provides company names (e.g., 'Tata Motors and Infosys'), make sure to split correctly and provide as a list of strings, each string as one company name"
            "Any tickers directly mentioned by the user should also be incorporated. "
            "If no specific entity is mentioned, strictly output an empty list []."
            "If only one company name/ticker, it should also be output as a list, with a single member."
        )
    )
    
    timeframe: int = Field(
        default=24, 
        description=(
            "The analysis lookback window for News/Twitter converted strictly to HOURS. "
            "Examples: 'last 2 days' = 48, 'past week' = 168, 'last month' = 720. "
            "Default to 24 if no specific time window is requested."
        )
    )
    
    run_news: bool = Field(
        description="Set to True if the query requires external context, headlines, or market catalysts."
    )
    
    run_twitter: bool = Field(
        description="Set to True ONLY if the user specifically asks for social sentiment, 'retail hype', or mentions Twitter/X."
    )
    
    run_technical: bool = Field(
        description="Set to True if the user asks for price action, patterns, support/resistance, or indicators."
    )
    
    run_fundamental: bool = Field(
        description="Set to True if the query focuses on 'fair value', 'intrinsic value', or financial health (DCF)."
    )
    
    run_montecarlo: bool = Field(
        description="Set to True if the user asks for 'risk', 'probability', or a 'Buy/Sell' recommendation."
    )

    interval: str = Field(
        default="5minute",
        description=(
            "The data interval for technical analysis. "
            "Rules: If user implies short-term/intraday (e.g., 'today', 'now'), use 'minute' or '5minute'. "
            "If user implies swing trading (e.g., 'this week'), use '60minute'. "
            "If user implies long-term/investing (e.g., 'trend', 'history'), use 'day'. "
            "Valid values: '5minute', '3minute', 'minute', '10minute', '15minute', '30minute', '60minute', 'day'."
        )
    )
    
    start_date: Optional[str] = Field(
        default_factory=lambda: (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
        description=(
            "The start date for analysis in ISO format (YYYY-MM-DD). "
            "Infer this from the user's query context. "
            "Examples: 'since Jan 2024' -> '2024-01-01'. 'Last year' -> date 365 days ago. "
            "If no date is implied, use one month ago as the start date."
        )
    )
    
    end_date: Optional[str] = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d"),
        description=(
            "The end date for analysis in ISO format (YYYY-MM-DD). "
            "Usually today's date unless the user asks for a specific past range (e.g., 'how did it do in 2022?'). "
            "If not specified, use today's date."
        )
    )

class Orchestrator:
    def __init__(self, model_name: str = "gpt-4o"):
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        self.router_chain = self.llm.with_structured_output(AgentRoutingDecision)

    def parse_query(self, query: str, state: StockAgentState) -> Dict[str, Any]:
        """Analyzes query and builds the execution plan."""
        decision = self._get_llm_decision(query, state)
               
        # 1. Handle End Date (Default to Now if None)
        if decision.end_date:
            try:
                # Attempt to parse full ISO format with time
                final_end_date = datetime.fromisoformat(decision.end_date)
                print(f"[DEBUG] Parsed end_date with time: {final_end_date}")
            except ValueError:
                final_end_date = datetime.now()
        else:
            final_end_date = datetime.now()

        # 2. Handle Start Date
        if decision.start_date:
            try:
                final_start_date = datetime.fromisoformat(decision.start_date)
                print(f"[DEBUG] Parsed start_date with time: {final_start_date}")
            except ValueError:
                # Fallback logic
                final_start_date = final_end_date - timedelta(days=100)
        else:
            # Smart defaults based on interval
            if decision.interval == 'day':
                final_start_date = final_end_date - timedelta(days=365)
            elif decision.interval in ['60minute', '30minute']:
                final_start_date = final_end_date - timedelta(days=60)
            else:
                # For intraday (1min - 15min), default to 5 days ago
                final_start_date = final_end_date - timedelta(days=5)

        # Safety: Ensure start is before end
        if final_start_date >= final_end_date:
            # If equal/inverted, fallback to 1 day gap
            final_start_date = final_end_date - timedelta(days=1)

        #   Ticker Count Check  
        if len(decision.tickers) != 1:
            print(f"[INFO] Ticker count is {len(decision.tickers)}. Disabling specialized agents.")
            decision.run_news = False
            decision.run_twitter = False
            decision.run_technical = False
            decision.run_fundamental = False
            decision.run_montecarlo = False

        #Process tickers and company names
        extracted_entities = get_bse_tickers(decision.tickers)
        extracted_company_names = []
        extracted_tickers = []
        for query, result in extracted_entities.items():
            extracted_company_names.append(result["company_name"])
            extracted_tickers.append(result["ticker"])

        target_ticker = extracted_tickers[0] if extracted_tickers else "UNKNOWN"

        # Pass parsed datetime objects to inputs
        agent_inputs = {
            "news_agent": {"ticker": target_ticker},
            "twitter_agent": {"ticker": target_ticker, "hours_delta": decision.timeframe},
            "technical_agent": TechnicalInput(
                ticker=target_ticker, 
                interval=decision.interval, 
                start_date=final_start_date.isoformat(),  
                end_date=final_end_date.isoformat()
            ),
            "fundamental_agent": FundamentalInput(tickers=extracted_tickers),
            "montecarlo_agent": MontecarloInput(ticker=target_ticker)
        }
        
        parsed_intent = {
            "decision": decision.dict(), 
            "agent_inputs": agent_inputs,
            "tickers": extracted_tickers,
            "company_names": extracted_company_names
        }
        
        return parsed_intent

    def _get_llm_decision(self, query: str, state: StockAgentState) -> AgentRoutingDecision:
        """Invoke LLM for routing decision or handle Kafka signals."""
        
        message_type = state.get("message_type", "terminal")
        
        #   KAFKA SIGNAL HANDLING (Short-circuits LLM)  
        if message_type == "technical_kafka":
            trigger_signal = state.get("trigger_signal", {})
            return AgentRoutingDecision(tickers=[trigger_signal.get("ticker")], timeframe=24, run_news=True, run_twitter=True, run_technical=False, run_fundamental=False, run_montecarlo=True)
        
        if message_type == "news_kafka":
            news_input = state.get("news_kafka_input", {})
            return AgentRoutingDecision(tickers=[news_input.get("ticker")], timeframe=24, run_news=False, run_twitter=False, run_technical=True, run_fundamental=False, run_montecarlo=True)
        
        #   LLM ROUTING PROMPT  
        now = datetime.now()
        current_date_str = now.strftime("%Y-%m-%d")
        current_time_str = now.strftime("%H:%M:%S")
        
        system_msg = f"""You are the **Stocks Orchestrator**, the brain of an autonomous financial system. 
Parse user intent into strict JSON for agent routing.

**CURRENT CONTEXT:**
- Date: {current_date_str}
- Time: {current_time_str} (Local)

### DATE & TIME LOGIC
- You must output precise ISO timestamps (YYYY-MM-DDTHH:MM:SS) if the user implies time.
- You must ensure that atleast 1 week data is returned, anything which implies less than that, parse the satrt date to a week earlier.
- **Example 1:** "Analyze Reliance today from 9:15 to 11:00" 
  -> start="{current_date_str}T09:15:00", end="{current_date_str}T11:00:00", interval="5minute"
- **Example 2:** "Last hour"
  -> start=[1 hour ago ISO], end=[now ISO], interval="minute"
- **Example 3:** "Daily chart for 2023"
  -> start="2023-01-01T00:00:00", end="2023-12-31T23:59:59", interval="day"
- If NO specific date/time is mentioned, leave `start_date` and `end_date` as null.

### AVAILABLE AGENTS & CAPABILITIES

1. **TECHNICAL_AGENT**:
   - **Capability:** Analyzes the specified interval OHLCV data from Zerodha. Calculates indicators (RSI, MACD, Bollinger Bands) and generates explicit BUY/SELL/HOLD signals with strength scores.
   - **Trigger:** When user asks for price action, trends, chart patterns, "Is it overbought?", or entry/exit timing.

2. **FUNDAMENTAL_AGENT**:
   - **Capability:** Performs deep quantitative valuation using Discounted Cash Flow (DCF) pipelines to determine Intrinsic Value and analyzes long-term financial health.
   - **Trigger:** When user asks for "fair value", "valuation", "long-term investment", "fundamentals", or "underpriced/overpriced".

3. **NEWS_AGENT**:
   - **Capability:** Aggregates real-time news and performs LLM-based sentiment classification (Bullish/Bearish/Neutral).
   - **Trigger:** When user asks for "news", "headlines", "recent events", or "why is the stock moving?".

4. **TWITTER_AGENT**:
   - **Capability:** Scrapes X (Twitter) to analyze retail sentiment, crowd hype, and FUD (Fear, Uncertainty, Doubt) over the last N hours.
   - **Trigger:** When user asks for social sentiment, "what people are saying", "hype", or specifically mentions Twitter/X.

5. **MONTE_CARLO_AGENT**:
   - **Capability:** Runs stochastic bootstrap simulations on historical log returns to calculate Value at Risk (VaR), Probability of Loss, and Best/Worst case scenarios.
   - **Trigger:** When user asks for "risk", "probability", "safety", "future projections", or asks for a trading decision ("Should I buy?") which *requires* risk assessment.

### ROUTING LOGIC RULES
1. **Company names/Ticker Entity Extraction:** Identify specific, individual company names or stock ticker symbols mentioned by the user.
   - **Multi-Entity Support:** If the user mentions multiple stocks (e.g., "Compare RELIANCE and TCS"), extract ALL of them into the list.
   - If the user provides company names (e.g., 'Tata Motors and Infosys'), make sure to split correctly and provide as a list of strings, each string as one company name
   - Any tickers directly mentioned by the user should also be incorporated. 
   - If only one company name/ticker, it should also be output as a list, with a single member.
   - If ambiguous or missing, output an empty list `[]`.

2. **Context Dependency:**
   - If the user asks **"Should I buy [Ticker]?"**: You MUST activate `Technical`, `News`, and `MonteCarlo` (Risk) at minimum.
   - If the user asks **"Is [Ticker] safe?"**: You MUST activate `MonteCarlo` (Risk) and `Fundamental` (Stability).

Analyze the query and generate the routing JSON."""
        
        try:
            return self.router_chain.invoke([
                ("system", system_msg),
                ("user", query)
            ])
        except Exception as e:
            print(f"[ERROR] LLM Routing failed: {e}")
            # Fallback #####Fix this
            ticker_matches = re.findall(r'\b([A-Z]{2,6})\b', query)
            fallback_tickers = ticker_matches if ticker_matches else ["RELIANCE"]
            return AgentRoutingDecision(tickers=fallback_tickers, timeframe=24, run_news=True, run_twitter=False, run_technical=False, run_fundamental=False, run_montecarlo=False, interval="day", start_date=None, end_date=None)

    def run(self, state: StockAgentState) -> Dict[str, Any]:
        """LangGraph node function."""
        query = state.get("query", "")
        parsed_intent = self.parse_query(query, state)
        
        if "ticker" not in state:
            state["ticker"] = []
        state.get("ticker", []).extend(parsed_intent["tickers"])
        
        return {
            "parsed_intent": parsed_intent,
            "tickers": parsed_intent["tickers"],
        }

if __name__ == "__main__":
    print("=" * 80)
    print("PATHWAY ORCHESTRATOR TEST SUITE (TIMESTAMPS)")
    print("=" * 80)
    
    orchestrator = Orchestrator(model_name="gpt-4o")
    
    # Test: Intraday Specific Time
    print("\n[TEST] Specific Time Range (Today 9:15 - 10:15)")
    state = {
        "message_type": "terminal",
        "query": "Check Reliance price action today between 9:15 AM and 10:15 AM",
    }
    result = orchestrator.run(state)
    inputs = result["parsed_intent"]["agent_inputs"]["technical_agent"]
    
    print(f"Query: {state['query']}")
    print(f"Start: {inputs.start_date} | End: {inputs.end_date}")
    
    # Validation
    assert inputs.start_date.hour == 9
    assert inputs.start_date.minute == 15
    assert inputs.end_date.hour == 10
    assert inputs.end_date.minute == 15
    
    print("Timestamp precision test passed.")