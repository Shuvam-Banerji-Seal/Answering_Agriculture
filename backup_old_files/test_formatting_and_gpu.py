#!/usr/bin/env python3
"""
Quick test script to verify formatting and GPU handling
"""

import sys
import os
sys.path.append('agri_bot_searcher/src')

def test_formatting():
    """Test text formatting with newlines"""
    print("🧪 Testing text formatting...")
    
    # Test text with various formatting
    test_text = """This is a test answer with multiple paragraphs.

This is the second paragraph with some formatting.

**Bold text** and *italic text* and `code text`.

Final paragraph with proper line breaks."""
    
    print("Original text:")
    print(repr(test_text))
    
    # Simulate the JavaScript formatting
    formatted = test_text.replace('\n', '<br>')
    print("\nFormatted text (what should appear in UI):")
    print(formatted)
    
    return test_text

def test_gpu_detection():
    """Test GPU detection and FAISS handling"""
    print("\n🖥️ Testing GPU detection...")
    
    try:
        import torch
        print(f"PyTorch available: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"GPU device: {torch.cuda.get_device_name(0)}")
            props = torch.cuda.get_device_properties(0)
            print(f"GPU memory: {props.total_memory / (1024**3):.1f} GB")
            print(f"Sufficient memory (>2GB): {props.total_memory > 2 * 1024**3}")
        
    except ImportError:
        print("PyTorch not available")
    
    # Test FAISS
    try:
        import faiss
        print(f"FAISS available: {faiss.__version__}")
        print(f"FAISS GPU support: {hasattr(faiss, 'StandardGpuResources')}")
    except ImportError:
        print("FAISS not available")

def test_web_search():
    """Test web search with new ddgs package"""
    print("\n🔍 Testing web search...")
    
    try:
        from ddgs import DDGS
        print("New ddgs package available")
        
        with DDGS() as ddgs:
            results = list(ddgs.text("agriculture soil health", max_results=2))
            print(f"Found {len(results)} results")
            if results:
                print(f"First result: {results[0].get('title', 'No title')}")
                
    except ImportError:
        try:
            from duckduckgo_search import DDGS
            print("Old duckduckgo_search package available (will show warnings)")
        except ImportError:
            print("No web search package available")

def main():
    """Run all tests"""
    print("🚀 Quick Test Suite for Enhanced RAG System")
    print("=" * 50)
    
    test_text = test_formatting()
    test_gpu_detection()
    test_web_search()
    
    print("\n" + "=" * 50)
    print("✅ Quick tests completed!")
    print("\nTo test the full system:")
    print("1. Start the web UI: python agri_bot_searcher/src/enhanced_web_ui.py")
    print("2. Open browser to http://localhost:5000")
    print("3. Ask a question and check if text has proper line breaks")

if __name__ == "__main__":
    main()
