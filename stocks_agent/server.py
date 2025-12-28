"""
Flask HTTP server for the StocksAgent system.
Exposes REST endpoints for querying the multi-agent analysis system.
"""

import sys
import os
import time
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
# Add parent directory to path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify

from stocks_agent.graph import get_compiled_graph
from stocks_agent.state import StockAgentState

# Initialize Flask app
app = Flask(__name__)

# Global state
graph = None
start_time = None
queries_processed = 0

# Available agents list
AVAILABLE_AGENTS = [
    "news_agent",
    "twitter_agent",
    "montecarlo_agent",
    "technical_agent",
    "fundamental_agent",
]


def init_graph():
    """Initialize the agent graph at startup."""
    global graph, start_time
    print("Initializing agent graph...")
    try:
        graph = get_compiled_graph()
        start_time = datetime.utcnow()
        print("Agent graph ready!")
        return True
    except Exception as e:
        print(f"Error initializing graph: {e}")
        return False


def run_query(query: str) -> dict:
    """
    Run a query through the agent graph.
    
    Args:
        query: User query string
        
    Returns:
        Dictionary with response data
    """
    global queries_processed
    
    # Initialize state with the query
    initial_state: StockAgentState = {
        "query": query,
        "ticker": [],
        "parsed_intent": {},
        "news_output": None,
        "twitter_output": None,
        "montecarlo_output": None,
        "technical_output": None,
        "fundamental_output": None,
        "final_response": None,
        "agent_contributions": [],
        "no_llm_flag": True
    }
    
    # Run the graph
    result = graph.invoke(initial_state)
    queries_processed += 1
    
    # Extract ticker from parsed intent if available
    parsed_intent = result.get("parsed_intent", {})
    decision = parsed_intent.get("decision", {})
    ticker = decision.get("ticker") if decision else None
    
    # If not in decision, try tickers list
    if not ticker:
        tickers = parsed_intent.get("tickers", [])
        ticker = tickers[0] if tickers else None
    
    return {
        "response": result.get("final_response", "No response generated."),
        "ticker": ticker,
        "agents_used": result.get("agent_contributions", []),
    }


@app.route("/query", methods=["POST"])
def query_endpoint():
    """
    POST /query
    
    Accept a query and return the agent response.
    
    Request body:
        {"query": "Analyze RELIANCE technical indicators"}
        
    Response:
        {"success": true, "response": "...", "ticker": "RELIANCE", "agents_used": [...]}
    """
    if graph is None:
        return jsonify({
            "success": False,
            "error": "Agent graph not initialized"
        }), 503
    
    # Get request data
    data = request.get_json()
    
    if not data or "query" not in data:
        return jsonify({
            "success": False,
            "error": "Missing 'query' field in request body"
        }), 400
    
    query = data["query"].strip()
    
    if not query:
        return jsonify({
            "success": False,
            "error": "Query cannot be empty"
        }), 400
    
    try:
        result = run_query(query)
        return jsonify({
            "success": True,
            **result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/health", methods=["GET"])
def health_endpoint():
    """
    GET /health
    
    Health check endpoint.
    
    Response:
        {"status": "healthy", "graph_ready": true}
    """
    return jsonify({
        "status": "healthy" if graph is not None else "unhealthy",
        "graph_ready": graph is not None
    })


@app.route("/status", methods=["GET"])
def status_endpoint():
    """
    GET /status
    
    System status with agent info.
    
    Response:
        {"agents": [...], "uptime": "...", "queries_processed": N}
    """
    uptime_seconds = None
    uptime_str = "N/A"
    
    if start_time:
        uptime_seconds = (datetime.utcnow() - start_time).total_seconds()
        hours, remainder = divmod(int(uptime_seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{hours}h {minutes}m {seconds}s"
    
    return jsonify({
        "agents": AVAILABLE_AGENTS,
        "uptime": uptime_str,
        "uptime_seconds": uptime_seconds,
        "queries_processed": queries_processed,
        "graph_ready": graph is not None,
        "start_time": start_time.isoformat() if start_time else None
    })


def main():
    """Main entry point for the Flask server."""
    # Initialize the graph
    if not init_graph():
        print("Failed to initialize graph. Exiting.")
        sys.exit(1)
    
    # Run the Flask app
    print(f"\nStarting Flask server on port 3000...")
    print("Endpoints:")
    print("  POST /query  - Submit a query")
    print("  GET  /health - Health check")
    print("  GET  /status - System status")
    print("-" * 50)
    
    app.run(host="0.0.0.0", port=3000, debug=False)


if __name__ == "__main__":
    main()

