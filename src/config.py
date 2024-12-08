"""
Module for managing application configuration settings.

This module provides Pydantic models for managing configuration settings related to
the LLM model, language preferences, and output directories. It ensures type safety
and validation for all configuration parameters.
"""

from pathlib import Path
from pydantic import BaseModel
from typing import Optional

class ModelConfig(BaseModel):
    """
    Configuration settings for the LLM model.
    
    Attributes:
        model_name (str): Name of the Ollama model to use (default: "llama3.2")
        temperature (float): Sampling temperature for text generation (default: 0.1)
        max_tokens (Optional[int]): Maximum number of tokens to generate (None for no limit)
        context_window (int): Size of the context window in tokens (default: 10000)
        overlap (int): Token overlap between chunks when splitting text (default: 200)
    """
    model_name: str = "llama3.2"
    temperature: float = 0.1
    max_tokens: Optional[int] = None
    context_window: int = 10000
    overlap: int = 200

class Config(BaseModel):
    """
    Main configuration class for the application.
    
    Attributes:
        model (ModelConfig): LLM model configuration settings
        language (str): Primary language for interactions (default: "de" for German)
        output_dir (Path): Directory for saving outputs and sessions
        verbose (bool): Whether to enable verbose logging (default: False)
    """
    model: ModelConfig = ModelConfig()
    language: str = "de"
    output_dir: Path = Path("outputs")
    verbose: bool = False
    
    class Config:
        """Inner configuration class for Pydantic settings"""
        arbitrary_types_allowed = True  # Allow Path objects