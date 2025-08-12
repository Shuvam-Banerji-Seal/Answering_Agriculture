"""
Sub-Query Generation Package

A comprehensive package for generating multiple sub-queries from a single query
to improve RAG (Retrieval-Augmented Generation) performance.
"""

from .base import SubQueryGenerator, SubQueryResult
from .ollama_generator import OllamaSubQueryGenerator
from .huggingface_generator import HuggingFaceSubQueryGenerator
from .factory import SubQueryGeneratorFactory

__version__ = "1.0.0"
__all__ = [
    "SubQueryGenerator",
    "SubQueryResult", 
    "OllamaSubQueryGenerator",
    "HuggingFaceSubQueryGenerator",
    "SubQueryGeneratorFactory"
]