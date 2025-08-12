"""
Ollama-based sub-query generator.
"""

import requests
import json
from typing import List, Dict, Any
from .base import SubQueryGenerator, SubQueryResult


class OllamaSubQueryGenerator(SubQueryGenerator):
    """Sub-query generator using Ollama."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.ollama_config = config.get('model', {}).get('ollama', {})
        self.base_url = self.ollama_config.get('base_url', 'http://localhost:11434')
        self.model_name = self.ollama_config.get('model_name', 'gemma2:2b')
        self.timeout = self.ollama_config.get('timeout', 30)
        
    def is_available(self) -> bool:
        """Check if Ollama is available and the model is loaded."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                return any(self.model_name in name for name in model_names)
            return False
        except Exception as e:
            self.logger.error(f"Failed to check Ollama availability: {e}")
            return False
    
    def generate_sub_queries(self, query: str) -> SubQueryResult:
        """Generate sub-queries using Ollama."""
        if not self.is_available():
            raise RuntimeError(f"Ollama is not available or model {self.model_name} is not loaded")
        
        prompt = self._create_prompt(query)
        
        # Prepare the request payload
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.get('generation', {}).get('temperature', 0.7),
                "num_predict": self.config.get('generation', {}).get('max_new_tokens', 1000),
            }
        }
        
        try:
            self.logger.info(f"Generating sub-queries for: {query}")
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            generated_text = result.get('response', '')
            
            # Parse the response to extract sub-queries
            sub_queries = self._parse_response(generated_text)
            
            if not sub_queries:
                self.logger.warning("No sub-queries extracted from response")
                sub_queries = [query]  # Fallback to original query
            
            self.logger.info(f"Generated {len(sub_queries)} sub-queries")
            
            return SubQueryResult(
                original_query=query,
                sub_queries=sub_queries,
                metadata={
                    'model': self.model_name,
                    'implementation': 'ollama',
                    'raw_response': generated_text,
                    'generation_config': payload['options']
                }
            )
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ollama request failed: {e}")
            raise RuntimeError(f"Failed to generate sub-queries with Ollama: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error in sub-query generation: {e}")
            raise
    
    def pull_model(self) -> bool:
        """Pull the model if it's not available."""
        try:
            self.logger.info(f"Pulling model {self.model_name}")
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": self.model_name},
                timeout=300  # 5 minutes timeout for model pulling
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to pull model {self.model_name}: {e}")
            return False