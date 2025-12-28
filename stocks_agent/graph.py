"""
LangGraph definition for the StocksAgent system.
Uses Send() mechanism for parallel agent execution.
"""

import sys
import os
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END, START
from langgraph.types import Send
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from state import StockAgentState
from orchestrator import Orchestrator
from agents.news_agent import NewsAgent
from agents.twitter_agent import TwitterAgent
from agents.montecarlo_agent import MontecarloAgent
from agents.technical_agent2 import TechnicalAgent
from agents.fundamental_agent import FundamentalAgent
from agents.explainability_agent import ExplainabilityAgent
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize agents
orchestrator = Orchestrator()
news_agent = NewsAgent()
twitter_agent = TwitterAgent()
montecarlo_agent = MontecarloAgent()
technical_agent = TechnicalAgent()
fundamental_agent = FundamentalAgent()
explainability_agent = ExplainabilityAgent()

AGENT_REGISTRY = {
    "news_agent": news_agent,
    "twitter_agent": twitter_agent,
    "montecarlo_agent": montecarlo_agent,
    "technical_agent": technical_agent,
    "fundamental_agent": fundamental_agent,
}


def orchestrator_node(state: StockAgentState) -> Dict[str, Any]:
    """Parse the query and determine which agents to invoke."""
    return orchestrator.run(state)


def route_to_agents(state: StockAgentState) -> List[Send]:
    """
    Convert orchestrator's boolean decision flags into Send() calls for parallel execution.
    """
    parsed_intent = state.get("parsed_intent", {})
    
    decision = parsed_intent.get("decision", {})
    agent_inputs = parsed_intent.get("agent_inputs", {})
    
    sends = []
    
    if decision.get("run_news", False):
        sends.append(Send("news_agent", {**state, "_agent_input": agent_inputs["news_agent"]}))
    
    if decision.get("run_twitter", False):
        sends.append(Send("twitter_agent", {**state, "_agent_input": agent_inputs["twitter_agent"]}))
    
    if decision.get("run_technical", False):
        sends.append(Send("technical_agent", {**state, "_agent_input": agent_inputs["technical_agent"]}))
    
    if decision.get("run_fundamental", False):
        sends.append(Send("fundamental_agent", {**state, "_agent_input": agent_inputs["fundamental_agent"]}))
    
    if decision.get("run_montecarlo", False):
        sends.append(Send("montecarlo_agent", {**state, "_agent_input": agent_inputs["montecarlo_agent"]}))
    
    if not sends:
        logger.warning("No agents invoked, going directly to explainability")
        sends.append(Send("explainability", {**state}))
    
    return sends


def news_agent_node(state: StockAgentState) -> Dict[str, Any]:
    """Execute news agent."""
    agent_input = state.get("_agent_input", {})
    return news_agent(agent_input, state)


def twitter_agent_node(state: StockAgentState) -> Dict[str, Any]:
    """Execute twitter agent."""
    agent_input = state.get("_agent_input", {})
    return twitter_agent(agent_input, state)


def montecarlo_agent_node(state: StockAgentState) -> Dict[str, Any]:
    """Execute montecarlo agent."""
    agent_input = state.get("_agent_input", {})
    return montecarlo_agent(agent_input, state)


def technical_agent_node(state: StockAgentState) -> Dict[str, Any]:
    """Execute technical agent."""
    agent_input = state.get("_agent_input", {})
    return technical_agent(agent_input, state)


def fundamental_agent_node(state: StockAgentState) -> Dict[str, Any]:
    """Execute fundamental agent."""
    agent_input = state.get("_agent_input", {})
    return fundamental_agent(agent_input, state)


def explainability_node(state: StockAgentState) -> Dict[str, Any]:
    """Aggregate all outputs and generate final response."""
    return explainability_agent.run(state)


def build_graph() -> StateGraph:
    """
    Build and compile the LangGraph for the StocksAgent system.
    
    Flow:
    1. START -> orchestrator (parse query)
    2. orchestrator -> Send() to multiple agents in parallel (based on decision flags)
    3. All parallel agents auto-join -> explainability (aggregate)
    4. explainability -> END
    """
    graph = StateGraph(StockAgentState)
    
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("news_agent", news_agent_node)
    graph.add_node("twitter_agent", twitter_agent_node)
    graph.add_node("montecarlo_agent", montecarlo_agent_node)
    graph.add_node("technical_agent", technical_agent_node)
    graph.add_node("fundamental_agent", fundamental_agent_node)
    graph.add_node("explainability", explainability_node)
    
    graph.add_edge(START, "orchestrator")
    
    graph.add_conditional_edges(
        "orchestrator",
        route_to_agents
    )
    
    graph.add_edge("news_agent", "explainability")
    graph.add_edge("twitter_agent", "explainability")
    graph.add_edge("montecarlo_agent", "explainability")
    graph.add_edge("technical_agent", "explainability")
    graph.add_edge("fundamental_agent", "explainability")
    
    graph.add_edge("explainability", END)
    
    return graph


def get_compiled_graph():
    """Get the compiled graph ready for invocation."""
    graph = build_graph()
    return graph.compile()


app = get_compiled_graph()
logger.info("Graph compiled successfully")


if __name__ == "__main__":
    logger.info(app.get_graph().draw_mermaid())
