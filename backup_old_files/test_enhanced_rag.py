#!/usr/bin/env python3
"""
Test script for Enhanced RAG System
Tests all components of the enhanced RAG integration
"""

import os
import sys
import json
import time
import logging
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

def setup_logging():
    """Setup basic logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def test_dependencies():
    """Test if all required dependencies are available"""
    print("🔍 Testing dependencies...")
    
    dependencies = {
        'numpy': 'numpy',
        'faiss-cpu': 'faiss',
        'sentence-transformers': 'sentence_transformers',
        'duckduckgo-search': 'duckduckgo_search',
        'flask': 'flask',
        'requests': 'requests'
    }
    
    missing = []
    for name, module in dependencies.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - Missing")
            missing.append(name)
    
    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("Please install them with: pip install " + " ".join(missing))
        return False
    else:
        print("✅ All dependencies available")
        return True

def test_ollama_connection():
    """Test Ollama connection and models"""
    print("\n🤖 Testing Ollama connection...")
    
    try:
        import requests
        
        # Test Ollama API
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            print("  ✓ Ollama API responding")
            
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            
            # Check for required models
            required_models = ['gemma3:1b', 'gemma3:27b']
            available_models = []
            missing_models = []
            
            for model in required_models:
                if any(model in name for name in model_names):
                    available_models.append(model)
                    print(f"  ✓ {model} available")
                else:
                    missing_models.append(model)
                    print(f"  ✗ {model} missing")
            
            if missing_models:
                print(f"\n⚠️  Missing models: {', '.join(missing_models)}")
                print("Download with: ollama pull " + " && ollama pull ".join(missing_models))
            
            return len(available_models) > 0
            
        else:
            print(f"  ✗ Ollama API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ✗ Ollama connection failed: {e}")
        print("  Make sure Ollama is running: ollama serve")
        return False

def test_embeddings_database():
    """Test embeddings database availability"""
    print("\n📚 Testing embeddings database...")
    
    embeddings_dir = "/store/Answering_Agriculture/agriculture_embeddings"
    
    if not os.path.exists(embeddings_dir):
        print(f"  ✗ Embeddings directory not found: {embeddings_dir}")
        return False
    
    print(f"  ✓ Embeddings directory exists: {embeddings_dir}")
    
    # Check for required files
    required_files = {
        'FAISS index': ['faiss_index.bin', 'faiss_index.index'],
        'Metadata': ['metadata.json', 'metadata.pkl']
    }
    
    all_good = True
    for file_type, filenames in required_files.items():
        found = False
        for filename in filenames:
            filepath = os.path.join(embeddings_dir, filename)
            if os.path.exists(filepath):
                print(f"  ✓ {file_type}: {filename}")
                found = True
                break
        
        if not found:
            print(f"  ✗ {file_type}: Missing (need one of: {', '.join(filenames)})")
            all_good = False
    
    return all_good

def test_enhanced_rag_system():
    """Test the enhanced RAG system components"""
    print("\n🚀 Testing Enhanced RAG System...")
    
    try:
        from enhanced_rag_system import EnhancedRAGSystem
        
        embeddings_dir = "/store/Answering_Agriculture/agriculture_embeddings"
        
        if not os.path.exists(embeddings_dir):
            print("  ✗ Cannot test - embeddings database not available")
            return False
        
        print("  📝 Initializing Enhanced RAG System...")
        rag_system = EnhancedRAGSystem(embeddings_dir)
        print("  ✓ Enhanced RAG System initialized")
        
        # Test query processing with a simple query
        print("  🔍 Testing query processing...")
        test_query = "What are basic farming techniques?"
        
        start_time = time.time()
        result = rag_system.process_query(
            user_query=test_query,
            num_sub_queries=2,
            db_chunks_per_query=2,
            web_results_per_query=2,
            synthesis_model="gemma3:1b"  # Use smaller model for testing
        )
        processing_time = time.time() - start_time
        
        print(f"  ✓ Query processed in {processing_time:.2f}s")
        print(f"  📊 Sub-queries generated: {len(result.get('sub_queries', []))}")
        print(f"  📚 Database chunks: {result.get('stats', {}).get('total_db_chunks', 0)}")
        print(f"  🌐 Web results: {result.get('stats', {}).get('total_web_results', 0)}")
        
        if result.get('final_answer'):
            print("  ✓ Final answer generated")
        else:
            print("  ⚠️  No final answer generated")
        
        return True
        
    except ImportError as e:
        print(f"  ✗ Enhanced RAG System import failed: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Enhanced RAG System test failed: {e}")
        return False

def test_web_ui():
    """Test web UI components"""
    print("\n🌐 Testing Web UI...")
    
    try:
        from enhanced_web_ui import app
        print("  ✓ Enhanced Web UI imported successfully")
        
        # Test if app can start (just import check)
        if hasattr(app, 'run'):
            print("  ✓ Flask app configured")
        else:
            print("  ✗ Flask app configuration issue")
            return False
        
        return True
        
    except ImportError as e:
        print(f"  ✗ Enhanced Web UI import failed: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Web UI test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 Enhanced RAG System - Integration Test")
    print("=" * 60)
    
    setup_logging()
    
    # Track test results
    tests = {
        'Dependencies': test_dependencies(),
        'Ollama Connection': test_ollama_connection(),
        'Embeddings Database': test_embeddings_database(),
        'Enhanced RAG System': test_enhanced_rag_system(),
        'Web UI': test_web_ui()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in tests.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Enhanced RAG system is ready to use.")
        print("\nTo start the system:")
        print("  cd /store/Answering_Agriculture")
        print("  ./start_agri_bot.sh")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please fix the issues above.")
        
        if not tests['Dependencies']:
            print("\n💡 Install missing dependencies first:")
            print("  ./install_agri_bot.sh")
        
        if not tests['Ollama Connection']:
            print("\n💡 Start Ollama and download models:")
            print("  ollama serve")
            print("  ollama pull gemma3:1b")
            print("  ollama pull gemma3:27b")
        
        if not tests['Embeddings Database']:
            print("\n💡 Embeddings database needed:")
            print("  Place your embeddings in: /store/Answering_Agriculture/agriculture_embeddings/")
            print("  Required files: faiss_index.bin, metadata.json")

if __name__ == "__main__":
    main()
