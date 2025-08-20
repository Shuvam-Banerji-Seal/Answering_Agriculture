#!/usr/bin/env python3
"""
Comprehensive test script for the sub-query generation system.
Tests both Ollama and HuggingFace implementations with various scenarios.
"""

import sys
import os
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from factory import SubQueryGeneratorFactory
    from base import SubQueryResult
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORTS_AVAILABLE = False

# Test configuration
TEST_QUERIES = [
    "When should I sow the rice seeds?",
    "How to improve soil fertility naturally?",
    "What are the benefits of organic farming?",
    "Why is protein content in rice low?",
    "Best practices for sustainable agriculture",
    "How does climate change affect crop yields?",
    "What fertilizers are best for wheat cultivation?",
    "When to harvest tomatoes for maximum yield?",
]

class TestRunner:
    """Test runner for sub-query generation system."""
    
    def __init__(self):
        self.results = {}
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for tests."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def print_header(self, title: str):
        """Print a formatted header."""
        print("\n" + "=" * 60)
        print(f" {title}")
        print("=" * 60)
    
    def print_subheader(self, title: str):
        """Print a formatted subheader."""
        print(f"\n--- {title} ---")
    
    def test_imports(self) -> bool:
        """Test if all required modules can be imported."""
        self.print_subheader("Testing Imports")
        
        if not IMPORTS_AVAILABLE:
            print("❌ Failed to import sub-query generation modules")
            print("   Make sure you're running from the correct directory")
            return False
        
        print("✅ All modules imported successfully")
        return True
    
    def test_availability(self) -> Dict[str, bool]:
        """Test which implementations are available."""
        self.print_subheader("Testing Implementation Availability")
        
        if not IMPORTS_AVAILABLE:
            return {}
        
        try:
            implementations = SubQueryGeneratorFactory.get_available_implementations()
            
            for impl, available in implementations.items():
                status = "✅" if available else "❌"
                print(f"{status} {impl.capitalize()}: {'Available' if available else 'Not available'}")
            
            return implementations
        except Exception as e:
            print(f"❌ Error checking availability: {e}")
            return {}
    
    def test_config_loading(self) -> bool:
        """Test configuration file loading."""
        self.print_subheader("Testing Configuration Loading")
        
        if not IMPORTS_AVAILABLE:
            return False
        
        config_path = Path(__file__).parent / "config.yaml"
        
        if not config_path.exists():
            print("❌ Config file not found")
            return False
        
        try:
            # Test loading with config file
            generator = SubQueryGeneratorFactory.create_generator(config_path=str(config_path))
            print("✅ Configuration loaded from file successfully")
            
            # Test loading with config dict
            config_dict = {
                'model': {'implementation': 'ollama'},
                'generation': {'num_sub_queries': 3},
                'logging': {'level': 'WARNING'}
            }
            generator = SubQueryGeneratorFactory.create_generator(config_dict=config_dict)
            print("✅ Configuration loaded from dictionary successfully")
            
            return True
        except Exception as e:
            print(f"❌ Configuration loading failed: {e}")
            return False
    
    def test_ollama_generation(self) -> bool:
        """Test Ollama sub-query generation."""
        self.print_subheader("Testing Ollama Generation")
        
        if not IMPORTS_AVAILABLE:
            return False
        
        config = {
            'model': {
                'implementation': 'ollama',
                'ollama': {
                    'model_name': 'gemma3:1b',
                    'base_url': 'http://localhost:11434',
                    'timeout': 30
                }
            },
            'generation': {
                'temperature': 0.7,
                'max_new_tokens': 500,
                'num_sub_queries': 3
            },
            'logging': {'level': 'WARNING'}
        }
        
        try:
            generator = SubQueryGeneratorFactory.create_generator(config_dict=config)
            
            if not generator.is_available():
                print("❌ Ollama generator not available")
                print("   Make sure Ollama is running: ollama serve")
                print("   And model is available: ollama pull gemma3:1b")
                return False
            
            # Test with a simple query
            test_query = "When should I plant rice?"
            start_time = time.time()
            result = generator.generate_sub_queries(test_query)
            end_time = time.time()
            
            print(f"✅ Ollama generation successful")
            print(f"   Query: {result.original_query}")
            print(f"   Generated {len(result.sub_queries)} sub-queries")
            print(f"   Time taken: {end_time - start_time:.2f} seconds")
            print(f"   Model: {result.metadata.get('model', 'unknown')}")
            
            # Display sub-queries
            for i, query in enumerate(result.sub_queries, 1):
                print(f"   {i}. {query}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ollama generation failed: {e}")
            return False
    
    def test_huggingface_generation(self) -> bool:
        """Test HuggingFace sub-query generation."""
        self.print_subheader("Testing HuggingFace Generation")
        
        if not IMPORTS_AVAILABLE:
            return False
        
        # Check if transformers is available
        try:
            import transformers
            import torch
        except ImportError:
            print("❌ HuggingFace dependencies not available")
            print("   Install with: pip install transformers torch accelerate bitsandbytes")
            return False
        
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
            'logging': {'level': 'WARNING'}
        }
        
        try:
            print("Loading HuggingFace model (this may take a while)...")
            generator = SubQueryGeneratorFactory.create_generator(config_dict=config)
            
            if not generator.is_available():
                print("❌ HuggingFace generator not available")
                return False
            
            # Test with a simple query
            test_query = "How to improve crop yields?"
            start_time = time.time()
            result = generator.generate_sub_queries(test_query)
            end_time = time.time()
            
            print(f"✅ HuggingFace generation successful")
            print(f"   Query: {result.original_query}")
            print(f"   Generated {len(result.sub_queries)} sub-queries")
            print(f"   Time taken: {end_time - start_time:.2f} seconds")
            print(f"   Model: {result.metadata.get('model', 'unknown')}")
            print(f"   Device: {result.metadata.get('device', 'unknown')}")
            
            # Display sub-queries
            for i, query in enumerate(result.sub_queries, 1):
                print(f"   {i}. {query}")
            
            # Cleanup
            generator.cleanup()
            return True
            
        except Exception as e:
            print(f"❌ HuggingFace generation failed: {e}")
            return False
    
    def test_response_parsing(self) -> bool:
        """Test response parsing with various formats."""
        self.print_subheader("Testing Response Parsing")
        
        if not IMPORTS_AVAILABLE:
            return False
        
        from base import SubQueryGenerator
        
        # Mock generator for testing
        class MockGenerator(SubQueryGenerator):
            def generate_sub_queries(self, query):
                pass
            def is_available(self):
                return True
        
        generator = MockGenerator({})
        
        # Test different response formats
        test_responses = [
            # Quoted format
            '''1. "What is the optimal planting time for rice cultivation?"
2. "Rice seeding schedule and timing recommendations"
3. "Best time to plant rice seeds in the field"''',
            
            # Simple numbered format
            '''1. What are the main causes of low protein in rice?
2. How does rice protein compare to other grains?
3. What affects protein content in rice cultivation?''',
            
            # Parentheses format
            '''1) Protein deficiency in rice grains
2) Rice nutritional content analysis
3) Factors affecting rice protein levels''',
            
            # Mixed format with extra text
            '''Here are the variations:

1. Optimal timing for rice seed sowing
2. When to plant rice for best results
3. Rice planting schedule recommendations

These should help with retrieval.''',
        ]
        
        all_passed = True
        for i, response in enumerate(test_responses, 1):
            queries = generator._parse_response(response)
            expected_count = 3
            
            if len(queries) == expected_count and all(len(q) > 5 for q in queries):
                print(f"✅ Test {i}: Parsed {len(queries)} queries correctly")
                print(f"   Example: {queries[0]}")
            else:
                print(f"❌ Test {i}: Expected {expected_count} queries, got {len(queries)}")
                all_passed = False
        
        return all_passed
    
    def test_multiple_queries(self, implementation: str = 'ollama') -> bool:
        """Test generation with multiple different queries."""
        self.print_subheader(f"Testing Multiple Queries ({implementation})")
        
        if not IMPORTS_AVAILABLE:
            return False
        
        config = {
            'model': {'implementation': implementation},
            'generation': {'num_sub_queries': 3, 'temperature': 0.7},
            'logging': {'level': 'WARNING'}
        }
        
        if implementation == 'ollama':
            config['model']['ollama'] = {
                'model_name': 'gemma3:1b',
                'base_url': 'http://localhost:11434',
                'timeout': 30
            }
        
        try:
            generator = SubQueryGeneratorFactory.create_generator(config_dict=config)
            
            if not generator.is_available():
                print(f"❌ {implementation} generator not available")
                return False
            
            results = []
            total_time = 0
            
            for query in TEST_QUERIES[:3]:  # Test first 3 queries
                try:
                    start_time = time.time()
                    result = generator.generate_sub_queries(query)
                    end_time = time.time()
                    
                    query_time = end_time - start_time
                    total_time += query_time
                    
                    results.append({
                        'query': query,
                        'sub_queries': result.sub_queries,
                        'time': query_time,
                        'success': True
                    })
                    
                    print(f"✅ \"{query}\" -> {len(result.sub_queries)} sub-queries ({query_time:.2f}s)")
                    
                except Exception as e:
                    print(f"❌ \"{query}\" -> Failed: {e}")
                    results.append({
                        'query': query,
                        'success': False,
                        'error': str(e)
                    })
            
            successful = sum(1 for r in results if r.get('success', False))
            print(f"\n📊 Results: {successful}/{len(results)} successful")
            print(f"⏱️  Average time: {total_time/len(results):.2f}s per query")
            
            # Cleanup if needed
            if hasattr(generator, 'cleanup'):
                generator.cleanup()
            
            return successful > 0
            
        except Exception as e:
            print(f"❌ Multiple query test failed: {e}")
            return False
    
    def test_cli_interface(self) -> bool:
        """Test the CLI interface."""
        self.print_subheader("Testing CLI Interface")
        
        try:
            # Test help
            import subprocess
            result = subprocess.run([
                sys.executable, '-m', 'sub_query_generation.main', '--help'
            ], capture_output=True, text=True, cwd=Path(__file__).parent)
            
            if result.returncode == 0:
                print("✅ CLI help command works")
            else:
                print("❌ CLI help command failed")
                return False
            
            # Test availability check
            result = subprocess.run([
                sys.executable, '-m', 'sub_query_generation.main', '--check-availability'
            ], capture_output=True, text=True, cwd=Path(__file__).parent)
            
            if result.returncode == 0:
                print("✅ CLI availability check works")
                print("   Output:", result.stdout.strip()[:100] + "...")
            else:
                print("❌ CLI availability check failed")
                print("   Error:", result.stderr.strip())
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ CLI test failed: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling scenarios."""
        self.print_subheader("Testing Error Handling")
        
        if not IMPORTS_AVAILABLE:
            return False
        
        tests_passed = 0
        total_tests = 0
        
        # Test 1: Invalid configuration
        total_tests += 1
        try:
            config = {'model': {'implementation': 'invalid_impl'}}
            generator = SubQueryGeneratorFactory.create_generator(config_dict=config)
            print("❌ Should have failed with invalid implementation")
        except ValueError:
            print("✅ Correctly handled invalid implementation")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        # Test 2: Missing config file
        total_tests += 1
        try:
            generator = SubQueryGeneratorFactory.create_generator(config_path="nonexistent.yaml")
            print("❌ Should have failed with missing config file")
        except (FileNotFoundError, OSError):
            print("✅ Correctly handled missing config file")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        # Test 3: Empty query
        total_tests += 1
        try:
            config = {
                'model': {'implementation': 'ollama'},
                'generation': {'num_sub_queries': 3},
                'logging': {'level': 'WARNING'}
            }
            generator = SubQueryGeneratorFactory.create_generator(config_dict=config)
            
            if generator.is_available():
                result = generator.generate_sub_queries("")
                if result.sub_queries:
                    print("✅ Handled empty query gracefully")
                    tests_passed += 1
                else:
                    print("❌ Empty query not handled properly")
            else:
                print("⚠️  Skipping empty query test (generator not available)")
                tests_passed += 1  # Don't penalize for unavailable generator
        except Exception as e:
            print(f"❌ Empty query test failed: {e}")
        
        print(f"📊 Error handling: {tests_passed}/{total_tests} tests passed")
        return tests_passed == total_tests
    
    def run_all_tests(self):
        """Run all tests and provide a summary."""
        self.print_header("SUB-QUERY GENERATION SYSTEM TEST SUITE")
        
        # Track test results
        test_results = {}
        
        # Run tests
        test_results['imports'] = self.test_imports()
        
        if test_results['imports']:
            implementations = self.test_availability()
            test_results['config'] = self.test_config_loading()
            test_results['parsing'] = self.test_response_parsing()
            test_results['error_handling'] = self.test_error_handling()
            test_results['cli'] = self.test_cli_interface()
            
            # Test implementations that are available
            if implementations.get('ollama', False):
                test_results['ollama'] = self.test_ollama_generation()
                test_results['ollama_multiple'] = self.test_multiple_queries('ollama')
            else:
                print("\n⚠️  Skipping Ollama tests (not available)")
                test_results['ollama'] = None
                test_results['ollama_multiple'] = None
            
            if implementations.get('huggingface', False):
                test_results['huggingface'] = self.test_huggingface_generation()
            else:
                print("\n⚠️  Skipping HuggingFace tests (not available)")
                test_results['huggingface'] = None
        
        # Print summary
        self.print_header("TEST SUMMARY")
        
        passed = 0
        total = 0
        
        for test_name, result in test_results.items():
            if result is not None:
                total += 1
                if result:
                    passed += 1
                    status = "✅ PASS"
                else:
                    status = "❌ FAIL"
            else:
                status = "⚠️  SKIP"
            
            print(f"{status} {test_name.replace('_', ' ').title()}")
        
        print(f"\n📊 Overall Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! The sub-query generation system is working correctly.")
            return 0
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
            return 1

def main():
    """Main function to run tests."""
    runner = TestRunner()
    return runner.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())