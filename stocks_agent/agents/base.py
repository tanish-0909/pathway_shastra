"""
Base agent class that all StocksAgent agents inherit from.
"""

import sys
import os

# Add parent directory to path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from abc import ABC, abstractmethod
from typing import Dict, Any, Type, Union
from pydantic import BaseModel

from state import StockAgentState


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the StocksAgent system.
    Each agent must implement the `run` method and define its input/output schemas.
    """
    
    name: str = "base_agent"
    description: str = "Base agent class"
    
    # Subclasses should override these with their specific schema classes
    input_schema: Type[BaseModel] = None
    output_schema: Type[BaseModel] = None
    
    @abstractmethod
    def run(self, input_data: Any, state: StockAgentState) -> Dict[str, Any]:
        """
        Execute the agent's logic.
        
        Args:
            input_data: Validated Pydantic model instance matching input_schema
            state: Current overall agent state
            
        Returns:
            Dictionary with updates to apply to the state
        """
        pass
    
    def validate_input(self, input_data: Union[Dict[str, Any], BaseModel]) -> BaseModel:
        """
        Validate input data against the input schema.
        Accepts either a Dictionary OR a Pydantic Model.
        
        Args:
            input_data: Raw input dictionary or Pydantic Object
            
        Returns:
            Validated Pydantic model instance
        """
        if self.input_schema is None:
            raise NotImplementedError(f"{self.name} must define input_schema")
        
        # If input is already a Pydantic object of the correct type, return it.
        if isinstance(input_data, self.input_schema):
            return input_data
            
        # If input is a generic Pydantic object, dump it to dict first
        if isinstance(input_data, BaseModel):
            return self.input_schema(**input_data.model_dump())

        # If input is a Dict, unpack it
        return self.input_schema(**input_data)
    
    def validate_output(self, output_data: Dict[str, Any]) -> BaseModel:
        """
        Validate output data against the output schema.
        
        Args:
            output_data: Raw output dictionary
            
        Returns:
            Validated Pydantic model instance
        """
        if self.output_schema is None:
            raise NotImplementedError(f"{self.name} must define output_schema")
        return self.output_schema(**output_data)
    
    def __call__(self, input_data: Union[Dict[str, Any], BaseModel], state: StockAgentState) -> Dict[str, Any]:
        """
        Make the agent callable. Validates input, runs, and validates output.
        """
        # Validate input (Returns the Pydantic Object)
        validated_input = self.validate_input(input_data)
        
        # Run the agent with validated input as dict (allows ["key"] and .get() access)
        result = self.run(validated_input.model_dump(), state)
        
        return result