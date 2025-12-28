"""
Main entry point for the StocksAgent terminal interface.
Simple input/output loop for testing the agent system.
"""

import sys
import os
import json

# Add parent directory to path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stocks_agent.graph import get_compiled_graph
from stocks_agent.state import StockAgentState
from dotenv import load_dotenv
load_dotenv()

def print_banner():
    """Print welcome banner."""
    print("\n" + "=" * 60)
    print("       STOCKS AGENT - Multi-Agent Analysis System")
    print("=" * 60)
    print("\nAvailable agents:")
    print("  - News Agent: Analyzes news sentiment")
    print("  - Twitter Agent: Social media sentiment")
    print("  - Monte Carlo Agent: Risk simulations")
    print("  - Technical Agent: Technical indicators")
    print("  - Fundamental Agent: Company fundamentals")
    print("\nType 'exit' or 'quit' to exit.\n")
    print("-" * 60)


def run_query(graph, query: str) -> str:
    """
    Run a query through the agent graph.
    
    Args:
        graph: Compiled LangGraph
        query: User query string
        
    Returns:
        Final response string
    """
    # Initialize state with the query
    initial_state: StockAgentState = {
        "ticker": [],
        "query": query,
        "parsed_intent": {},
        "news_output": None,
        "twitter_output": None,
        "montecarlo_output": None,
        "technical_output": None,
        "fundamental_output": None,
        "final_response": None,
        "agent_contributions": []
    }
    
    # Run the graph
    result = graph.invoke(initial_state)
    # print(result)
    # print(json.dumps(result, indent=4, default=str))
    
    return result.get("final_response", "No response generated.")


def main():
    """Main terminal loop."""
    print_banner()
    
    # Compile the graph once
    print("Initializing agent graph...")
    try:
        graph = get_compiled_graph()
        # mermaid_code = graph.get_graph().draw_mermaid()
        # print(mermaid_code)
        print("Agent graph ready!\n")
    except Exception as e:
        print(f"Error initializing graph: {e}")
        sys.exit(1)
    
    # Main loop
    while True:
        try:
            # Get user input
            query = input("\nEnter your query: ").strip()
            
            # Check for exit commands
            if query.lower() in ["exit", "quit", "q"]:
                print("\nGoodbye!")
                break
            
            # Skip empty queries
            if not query:
                print("Please enter a query.")
                continue
            
            # Run the query
            print("\nProcessing your query...")
            print("-" * 60)
            
            response = run_query(graph, query)
            # print(response.keys())
            response["technical_output"]["json_data"]={}
            print(json.dumps(response, indent=4))
            
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye! ")
            break
        except Exception as e:
            print(f"\n Error processing query: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()

