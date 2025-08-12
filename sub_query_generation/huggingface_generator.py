"""
HuggingFace-based sub-query generator.
"""

import torch
from typing import List, Dict, Any, Optional
from .base import SubQueryGenerator, SubQueryResult


class HuggingFaceSubQueryGenerator(SubQueryGenerator):
    """Sub-query generator using HuggingFace transformers."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.hf_config = config.get('model', {}).get('huggingface', {})
        self.model_id = self.hf_config.get('model_id', 'google/gemma-2-2b-it')
        self.device = self._get_device()
        
        self.tokenizer = None
        self.model = None
        self._load_model()
    
    def _get_device(self) -> torch.device:
        """Determine the appropriate device."""
        device_config = self.hf_config.get('device', 'auto')
        
        if device_config == 'auto':
            if torch.cuda.is_available():
                return torch.device('cuda')
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return torch.device('mps')
            else:
                return torch.device('cpu')
        else:
            return torch.device(device_config)
    
    def _get_torch_dtype(self):
        """Get the appropriate torch dtype."""
        dtype_str = self.hf_config.get('torch_dtype', 'bfloat16')
        dtype_map = {
            'float16': torch.float16,
            'bfloat16': torch.bfloat16,
            'float32': torch.float32
        }
        return dtype_map.get(dtype_str, torch.bfloat16)
    
    def _load_model(self):
        """Load the tokenizer and model."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
            
            self.logger.info(f"Loading model {self.model_id}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_id,
                padding_side="left"
            )
            
            # Configure quantization if enabled
            quantization_config = None
            if self.hf_config.get('use_quantization', False):
                bits = self.hf_config.get('quantization_bits', 8)
                if bits == 8:
                    quantization_config = BitsAndBytesConfig(load_in_8bit=True)
                elif bits == 4:
                    quantization_config = BitsAndBytesConfig(load_in_4bit=True)
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                torch_dtype=self._get_torch_dtype(),
                quantization_config=quantization_config,
                device_map="auto" if quantization_config else None
            )
            
            if not quantization_config:
                self.model = self.model.to(self.device)
            
            self.logger.info(f"Model loaded successfully on {self.device}")
            
        except ImportError as e:
            self.logger.error("Required packages not installed. Install with: pip install transformers torch accelerate bitsandbytes")
            raise ImportError("Missing required packages for HuggingFace generator") from e
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if the model is loaded and available."""
        return self.model is not None and self.tokenizer is not None
    
    def generate_sub_queries(self, query: str) -> SubQueryResult:
        """Generate sub-queries using HuggingFace model."""
        if not self.is_available():
            raise RuntimeError("HuggingFace model is not loaded")
        
        prompt = self._create_prompt(query)
        
        # Format as chat template
        dialogue_template = [
            {"role": "user", "content": prompt}
        ]
        
        formatted_prompt = self.tokenizer.apply_chat_template(
            conversation=dialogue_template,
            tokenize=False,
            add_generation_prompt=True
        )
        
        try:
            self.logger.info(f"Generating sub-queries for: {query}")
            
            # Tokenize input
            input_ids = self.tokenizer(formatted_prompt, return_tensors="pt").to(self.device)
            
            # Generate response
            generation_config = self.config.get('generation', {})
            with torch.no_grad():
                outputs = self.model.generate(
                    **input_ids,
                    temperature=generation_config.get('temperature', 0.7),
                    do_sample=generation_config.get('do_sample', True),
                    max_new_tokens=generation_config.get('max_new_tokens', 1000),
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            output_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the original prompt from the output
            generated_text = output_text.replace(formatted_prompt, '').strip()
            
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
                    'model': self.model_id,
                    'implementation': 'huggingface',
                    'device': str(self.device),
                    'raw_response': generated_text,
                    'generation_config': generation_config
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate sub-queries: {e}")
            raise RuntimeError(f"Sub-query generation failed: {e}")
    
    def cleanup(self):
        """Clean up model resources."""
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()