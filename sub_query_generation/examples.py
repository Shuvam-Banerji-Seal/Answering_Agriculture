"""
Example usage of the sub-query generation system.
"""

import os
from pathlib import Path
from .factory import SubQueryGeneratorFactory


def example_ollama():
    """Example using Ollama implementation."""
    print("=== Ollama Example ===")
    
    # Create config for Ollama
    config = {
        'model': {
            'implementation': 'ollama',
            'ollama': {
                'model_name': 'gemma2:2b',
                'base_url': 'http://localhost:11434',
                'timeout': 30
            }
        },
        'generation': {
            'temperature': 0.7,
            'max_new_tokens': 1000,
            'num_sub_queries': 5
        },
        'logging': {
            'level': 'INFO'
        }
    }
    
    try:
        generator = SubQueryGeneratorFactory.create_generator(config_dict=config)
        
        if not generator.is_available():
            print("Ollama is not available. Make sure Ollama is running and the model is pulled.")
            return
        
        query = "Why is the protein content in rice less than other grains?"
        result = generator.generate_sub_queries(query)
        
        print(f"Original Query: {result.original_query}")
        print("\nGenerated Sub-queries:")
        for i, sub_query in enumerate(result.sub_queries, 1):
            print(f"{i}. {sub_query}")
        
        print(f"\nModel used: {result.metadata.get('model')}")
        
    except Exception as e:
        print(f"Error with Ollama example: {e}")


def example_huggingface():
    """Example using HuggingFace implementation."""
    print("\n=== HuggingFace Example ===")
    
    # Create config for HuggingFace
    config = {
        'model': {
            'implementation': 'huggingface',
            'huggingface': {
                'model_id': 'google/gemma-2-2b-it',
                'use_quantization': True,
                'quantization_bits': 8,
                'device': 'auto',
                'torch_dtype': 'bfloat16'
            }
        },
        'generation': {
            'temperature': 0.7,
            'max_new_tokens': 1000,
            'num_sub_queries': 5
        },
        'logging': {
            'level': 'INFO'
        }
    }
    
    try:
        generator = SubQueryGeneratorFactory.create_generator(config_dict=config)
        
        if not generator.is_available():
            print("HuggingFace model is not available. Check your installation and dependencies.")
            return
        
        query = "What are the best practices for sustainable agriculture?"
        result = generator.generate_sub_queries(query)
        
        print(f"Original Query: {result.original_query}")
        print("\nGenerated Sub-queries:")
        for i, sub_query in enumerate(result.sub_queries, 1):
            print(f"{i}. {sub_query}")
        
        print(f"\nModel used: {result.metadata.get('model')}")
        print(f"Device: {result.metadata.get('device')}")
        
        # Cleanup resources
        generator.cleanup()
        
    except Exception as e:
        print(f"Error with HuggingFace example: {e}")


def example_config_file():
    """Example using configuration file."""
    print("\n=== Config File Example ===")
    
    config_path = Path(__file__).parent / "config.yaml"
    
    if not config_path.exists():
        print(f"Configuration file not found: {config_path}")
        return
    
    try:
        generator = SubQueryGeneratorFactory.create_generator(config_path=str(config_path))
        
        if not generator.is_available():
            print("Generator is not available. Check your configuration and dependencies.")
            return
        
        queries = [
            "How does climate change affect crop yields?",
            "What are the benefits of organic farming?",
            "Why do some plants grow better in certain soils?"
        ]
        
        for query in queries:
            print(f"\nProcessing: {query}")
            result = generator.generate_sub_queries(query)
            
            print("Sub-queries:")
            for i, sub_query in enumerate(result.sub_queries, 1):
                print(f"  {i}. {sub_query}")
        
        # Cleanup if HuggingFace
        if hasattr(generator, 'cleanup'):
            generator.cleanup()
            
    except Exception as e:
        print(f"Error with config file example: {e}")


def example_rag_integration():
    """Example showing how to integrate with RAG systems."""
    print("\n=== RAG Integration Example ===")
    
    # Simulate a simple RAG workflow
    config = {
        'model': {
            'implementation': 'ollama',
            'ollama': {
                'model_name': 'gemma2:2b',
                'base_url': 'http://localhost:11434'
            }
        },
        'generation': {
            'num_sub_queries': 3  # Fewer queries for this example
        },
        'logging': {
            'level': 'WARNING'  # Less verbose
        }
    }
    
    try:
        generator = SubQueryGeneratorFactory.create_generator(config_dict=config)
        
        if not generator.is_available():
            print("Generator not available for RAG example")
            return
        
        original_query = "How to improve soil fertility naturally?"
        result = generator.generate_sub_queries(original_query)
        
        print(f"Original Query: {original_query}")
        print("\nQueries for RAG retrieval:")
        
        # In a real RAG system, you would use these queries for document retrieval
        all_queries = [original_query] + result.sub_queries
        
        for i, query in enumerate(all_queries):
            print(f"Query {i+1}: {query}")
            # Here you would typically:
            # 1. Convert query to embeddings
            # 2. Search your vector database
            # 3. Retrieve relevant documents
            # 4. Combine results from all queries
        
        print(f"\nTotal queries for retrieval: {len(all_queries)}")
        print("This approach increases the chance of finding relevant documents!")
        
    except Exception as e:
        print(f"Error with RAG integration example: {e}")


def main():
    """Run all examples."""
    print("Sub-Query Generation Examples")
    print("=" * 40)
    
    # Check availability first
    implementations = SubQueryGeneratorFactory.get_available_implementations()
    print("Available implementations:")
    for impl, available in implementations.items():
        status = "✓" if available else "✗"
        print(f"  {status} {impl}")
    print()
    
    # Run examples based on availability
    if implementations.get('ollama', False):
        example_ollama()
        example_rag_integration()
    else:
        print("Skipping Ollama examples (not available)")
    
    if implementations.get('huggingface', False):
        example_huggingface()
    else:
        print("Skipping HuggingFace examples (not available)")
    
    example_config_file()


if __name__ == "__main__":
    main()