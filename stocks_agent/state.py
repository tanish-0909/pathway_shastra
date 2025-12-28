from typing import TypedDict, Optional, List, Dict, Any, Annotated
import operator
from langchain_core.messages import BaseMessage

def update_dict(current: Dict[str, Any], new_val: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optional: Reducer to merge dictionaries if you ever have multiple steps 
    updating the SAME output field (e.g. a 'Chart Pattern' node and 'Indicator' node 
    both writing to 'technical_output').
    """
    if current is None:
        return new_val
    return {**current, **new_val}

class StockAgentState(TypedDict, total=False):
    #   1. Shared Context (Optimization)  
    # Parsed once by the Orchestrator, read by everyone else.
    query: str
    ticker: List[str]            
    timeframe: str 
    
    #   2. Message Source (for Kafka integration)  
    # "terminal" - from terminal input (default)
    # "technical_kafka" - from indicators pipeline via Kafka
    # "news_kafka" - from summarized_news topic via Kafka
    message_type: str
    
    # Trade signal from indicators pipeline (when message_type == "technical_kafka")
    trigger_signal: Dict[str, Any]
    
    # News data from summarized_news topic (when message_type == "news_kafka")
    # Contains: title, url, sentiment, financial_metrics, impact_assessment, 
    # liquidity_impact, summary, key_points, article_id, publisher details
    news_kafka_input: Dict[str, Any]
    
    # 3. LLM State
    messages: Annotated[List[BaseMessage], operator.add]
    
    # 4. Agent Outputs
    parsed_intent: Dict[str, Any]
    
    news_output: Annotated[Optional[Dict[str, Any]], update_dict]
    twitter_output: Annotated[Optional[Dict[str, Any]], update_dict]
    montecarlo_output: Annotated[Optional[Dict[str, Any]], update_dict]
    technical_output: Annotated[Optional[Dict[str, Any]], update_dict]
    fundamental_output: Annotated[Optional[Dict[str, Any]], update_dict]
    
    # 5. Final Response
    final_response: Optional[str]
    
    # 6. Kafka Publishing Decision
    should_publish: bool  # Whether to publish to stock_analysis topic
    conflict_reason: Optional[str]  # Reason if not publishing
    
    # 7. Observability
    agent_contributions: Annotated[List[str], operator.add]
    
    # Track errors
    errors: Annotated[List[str], operator.add]

    #techncial agent flag for no-llm reasoning
    no_llm_flag: bool


# Alias for backward compatibility
AgentState = StockAgentState


class AgentInput(TypedDict):
    """
    Input passed to individual agents via Send().
    Contains the agent-specific input parameters.
    """
    agent_name: str
    input_data: Dict[str, Any]
    state: StockAgentState


