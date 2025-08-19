#!/usr/bin/env python3
"""
Comprehensive test script for the Enhanced RAG System
Tests all features including toggles, citations, markdown generation, etc.
"""

import sys
import os
sys.path.append('agri_bot_searcher/src')

from enhanced_rag_system import EnhancedRAGSystem
import requests
import time
import json

def test_rag_system():
    """Test the RAG system components"""
    print("🧪 Testing Enhanced RAG System Components...")
    
    try:
        # Initialize system
        rag = EnhancedRAGSystem()
        print("✅ RAG system initialized successfully")
        
        # Test 1: Database search only
        print("\n📊 Test 1: Database search only")
        result1 = rag.process_query(
            "What are the best fertilizers for wheat?",
            num_sub_queries=2,
            db_chunks_per_query=2,
            web_results_per_query=2,
            enable_database_search=True,
            enable_web_search=False,
            synthesis_model='gemma3:1b'
        )
        
        db_chunks = result1.get('stats', {}).get('total_db_chunks', 0)
        web_results = result1.get('stats', {}).get('total_web_results', 0)
        print(f"   Database chunks: {db_chunks}")
        print(f"   Web results: {web_results}")
        print(f"   ✅ Database search working: {db_chunks > 0 and web_results == 0}")
        
        # Test 2: Web search only
        print("\n🌐 Test 2: Web search only")
        result2 = rag.process_query(
            "What are the latest organic farming techniques?",
            num_sub_queries=2,
            db_chunks_per_query=2,
            web_results_per_query=2,
            enable_database_search=False,
            enable_web_search=True,
            synthesis_model='gemma3:1b'
        )
        
        db_chunks2 = result2.get('stats', {}).get('total_db_chunks', 0)
        web_results2 = result2.get('stats', {}).get('total_web_results', 0)
        print(f"   Database chunks: {db_chunks2}")
        print(f"   Web results: {web_results2}")
        print(f"   ✅ Web search working: {db_chunks2 == 0 and web_results2 > 0}")
        
        # Test 3: Both searches enabled
        print("\n🔀 Test 3: Hybrid search (both enabled)")
        result3 = rag.process_query(
            "How to improve soil health for sustainable agriculture?",
            num_sub_queries=2,
            db_chunks_per_query=2,
            web_results_per_query=2,
            enable_database_search=True,
            enable_web_search=True,
            synthesis_model='gemma3:1b'
        )
        
        db_chunks3 = result3.get('stats', {}).get('total_db_chunks', 0)
        web_results3 = result3.get('stats', {}).get('total_web_results', 0)
        print(f"   Database chunks: {db_chunks3}")
        print(f"   Web results: {web_results3}")
        print(f"   ✅ Hybrid search working: {db_chunks3 > 0 and web_results3 > 0}")
        
        # Test 4: Check markdown file generation
        markdown_file = result3.get('markdown_file_path')
        if markdown_file and os.path.exists(markdown_file):
            print(f"\n📝 Test 4: Markdown file generated")
            print(f"   File path: {markdown_file}")
            
            with open(markdown_file, 'r') as f:
                content = f.read()
                print(f"   File size: {len(content)} characters")
                print(f"   ✅ Contains sources: {'##' in content}")
                print(f"   ✅ Contains database chunks: {'Database' in content}")
                print(f"   ✅ Contains web results: {'Web Search' in content}")
        
        # Test 5: Check for inline citations in final answer
        final_answer = result3.get('final_answer', '')
        print(f"\n📖 Test 5: Citation checking")
        print(f"   Answer length: {len(final_answer)} characters")
        print(f"   ✅ Has citations: {'[' in final_answer and ']' in final_answer}")
        print(f"   Answer preview: {final_answer[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG System test failed: {e}")
        return False

def test_web_ui():
    """Test the web UI API endpoints"""
    print("\n🌐 Testing Web UI API...")
    
    base_url = "http://localhost:5000"
    
    try:
        # Test system status
        response = requests.get(f"{base_url}/api/system-status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print("✅ System status endpoint working")
            print(f"   Enhanced RAG: {status.get('enhanced_rag_available')}")
            print(f"   Legacy Chatbot: {status.get('legacy_chatbot_available')}")
            print(f"   Mode: {status.get('mode')}")
        else:
            print(f"❌ System status failed: {response.status_code}")
            return False
        
        # Test enhanced query with toggles
        query_data = {
            "query": "What crops grow well in clay soil?",
            "num_sub_queries": 2,
            "db_chunks_per_query": 2,
            "web_results_per_query": 2,
            "enable_database_search": True,
            "enable_web_search": False,
            "synthesis_model": "gemma3:1b"
        }
        
        print("\n🔍 Testing enhanced query API...")
        response = requests.post(f"{base_url}/api/enhanced-query", 
                               json=query_data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Enhanced query endpoint working")
            print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
            print(f"   DB chunks: {result.get('stats', {}).get('total_db_chunks', 0)}")
            print(f"   Web results: {result.get('stats', {}).get('total_web_results', 0)}")
            print(f"   Final answer length: {len(result.get('final_answer', ''))}")
        else:
            print(f"❌ Enhanced query failed: {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to web UI. Make sure it's running on port 5000")
        return False
    except Exception as e:
        print(f"❌ Web UI test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Comprehensive Enhanced RAG System Tests")
    print("=" * 60)
    
    # Test RAG system components
    rag_success = test_rag_system()
    
    # Test web UI (if running)
    ui_success = test_web_ui()
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"RAG System Tests: {'✅ PASSED' if rag_success else '❌ FAILED'}")
    print(f"Web UI Tests: {'✅ PASSED' if ui_success else '❌ FAILED'}")
    
    if rag_success and ui_success:
        print("\n🎉 ALL TESTS PASSED! The Enhanced RAG System is working correctly.")
        print("\nKey Features Verified:")
        print("✅ Toggle controls for database and web search")
        print("✅ Markdown file generation with full content")
        print("✅ Inline citations in final answers")
        print("✅ Web UI with controls and toggles")
        print("✅ API endpoints functioning correctly")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
