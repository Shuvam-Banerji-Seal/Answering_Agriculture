"""
Factory for creating sub-query generators.
"""

import yaml
import logging
from typing import Dict, Any
from .base import SubQueryGenerator
from .ollama_generator import OllamaSubQueryGenerator
from .huggingface_generator import HuggingFaceSubQueryGenerator


class SubQueryGeneratorFactory:
    """Factory for creating sub-query generators."""
    
    @staticmethod
    def create_generator(config_path: str = None, config_dict: Dict[str, Any] = None) -> SubQueryGenerator:
        """
        Create a sub-query generator based on configuration.
        
        Args:
            config_path: Path to YAML configuration file
            config_dict: Configuration dictionary (takes precedence over config_path)
            
        Returns:
            SubQueryGenerator instance
        """
        if config_dict is None:
            if config_path is None:
                raise ValueError("Either config_path or config_dict must be provided")
            
            with open(config_path, 'r') as f:
                config_dict = yaml.safe_load(f)
        
        # Setup logging
        logging_config = config_dict.get('logging', {})
        logging.basicConfig(
            level=getattr(logging, logging_config.get('level', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename=logging_config.get('file')
        )
        
        implementation = config_dict.get('model', {}).get('implementation', 'ollama')
        
        if implementation == 'ollama':
            return OllamaSubQueryGenerator(config_dict)
        elif implementation == 'huggingface':
            return HuggingFaceSubQueryGenerator(config_dict)
        else:
            raise ValueError(f"Unknown implementation: {implementation}")
    
    @staticmethod
    def get_available_implementations() -> Dict[str, bool]:
        """Check which implementations are available."""
        implementations = {}
        
        # Check Ollama
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            implementations['ollama'] = response.status_code == 200
        except:
            implementations['ollama'] = False
        
        # Check HuggingFace
        try:
            import transformers
            import torch
            implementations['huggingface'] = True
        except ImportError:
            implementations['huggingface'] = False
        
        return implementations