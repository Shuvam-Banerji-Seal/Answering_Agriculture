"""
Test script for the sub-query generation system.
"""

import sys
import json
from pathlib import Path
from .factory import SubQueryGeneratorFactory


def test_availability():
    """Test which implementations are available."""
    print("Testing implementation availability...")
    implementations = SubQueryGeneratorFactory.get_available_implementations()
    
    for impl, available in implementations.items():
        status = "✓ Available" if available else "✗ Not available"
        print(f"  {impl}: {status}")
    
    return implementations


def test_ollama():
    """Test Ollama implementation."""
    print("\nTesting Ollama implementation...")
    
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
            'max_new_tokens': 500,
            'num_sub_queries': 3
        },
        'logging': {
            'level': 'WARNING'
        }
    }
    
    try:
        generator = SubQueryGeneratorFactory.create_generator(config_dict=config)
        
        if not generator.is_available():
            print("  ✗ Ollama not available")
            return False
        
        query = "What are the benefits of organic farming?"
        result = generator.generate_sub_queries(query)
        
        print(f"  ✓ Generated {len(result.sub_queries)} sub-queries")
        print(f"  Original: {result.original_query}")
        for i, sub_query in enumerate(result.sub_queries, 1):
            print(f"    {i}. {sub_query}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Ollama test failed: {e}")
        return False


def test_huggingface():
    """Test HuggingFace implementation."""
    print("\nTesting HuggingFace implementation...")
    
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
            'max_new_tokens': 500,
            'num_sub_queries': 3
        },
        'logging': {
            'level': 'WARNING'
        }
    }
    
    try:
        generator = SubQueryGeneratorFactory.create_generator(config_dict=config)
        
        if not generator.is_available():
            print("  ✗ HuggingFace model not available")
            return False
        
        query = "How does climate change affect agriculture?"
        result = generator.generate_sub_queries(query)
        
        print(f"  ✓ Generated {len(result.sub_queries)} sub-queries")
        print(f"  Original: {result.original_query}")
        for i, sub_query in enumerate(result.sub_queries, 1):
            print(f"    {i}. {sub_query}")
        
        # Cleanup
        generator.cleanup()
        return True
        
    except Exception as e:
        print(f"  ✗ HuggingFace test failed: {e}")
        return False


def test_config_file():
    """Test configuration file loading."""
    print("\nTesting configuration file...")
    
    config_path = Path(__file__).parent / "config.yaml"
    
    if not config_path.exists():
        print("  ✗ Config file not found")
        return False
    
    try:
        generator = SubQueryGeneratorFactory.create_generator(config_path=str(config_path))
        print("  ✓ Configuration loaded successfully")
        
        if generator.is_available():
            print("  ✓ Generator is available")
            return True
        else:
            print("  ✗ Generator not available (check dependencies)")
            return False
            
    except Exception as e:
        print(f"  ✗ Config test failed: {e}")
        return False


def test_parsing():
    """Test response parsing logic."""
    print("\nTesting response parsing...")
    
    # Mock generator for testing parsing
    from .base import SubQueryGenerator
    
    class MockGenerator(SubQueryGenerator):
        def generate_sub_queries(self, query):
            pass
        def is_available(self):
            return True
    
    generator = MockGenerator({})
    
    # Test different response formats
    test_responses = [
        '''1. "What factors contribute to reduced protein levels in rice grains?"
2. "Rice protein yield and nutritional content analysis"
3. "Why doesn't rice have much protein?"''',
        
        '''1. What are the main causes of low protein in rice?
2. How does rice protein compare to other grains?
3. What affects protein content in rice cultivation?''',
        
        '''1) Protein deficiency in rice grains
2) Rice nutritional content analysis
3) Factors affecting rice protein levels'''
    ]
    
    for i, response in enumerate(test_responses, 1):
        queries = generator._parse_response(response)
        print(f"  Test {i}: Parsed {len(queries)} queries")
        if queries:
            print(f"    Example: {queries[0]}")
    
    return True


def main():
    """Run all tests."""
    print("Sub-Query Generation System Test")
    print("=" * 40)
    
    results = {}
    
    # Test availability
    implementations = test_availability()
    
    # Test implementations
    if implementations.get('ollama', False):
        results['ollama'] = test_ollama()
    else:
        print("\nSkipping Ollama test (not available)")
        results['ollama'] = False
    
    if implementations.get('huggingface', False):
        results['huggingface'] = test_huggingface()
    else:
        print("\nSkipping HuggingFace test (not available)")
        results['huggingface'] = False
    
    # Test config and parsing
    results['config'] = test_config_file()
    results['parsing'] = test_parsing()
    
    # Summary
    print("\n" + "=" * 40)
    print("Test Summary:")
    for test, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {test}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    print(f"\nPassed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())