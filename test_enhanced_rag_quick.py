#!/usr/bin/env python3
"""
Quick Enhanced RAG System Test
Tests core functionality without heavy model loading
"""

import sys
import os
sys.path.append('agri_bot_searcher/src')

def test_web_content_extraction():
    """Test web content extraction"""
    print("🌐 Testing Web Content Extraction...")
    
    try:
        from enhanced_rag_system import WebSearcher
        
        searcher = WebSearcher()
        results = searcher.search('soil health agriculture farming', 2)
        
        print(f"✅ Found {len(results)} web results")
        
        total_content = 0
        for i, result in enumerate(results):
            content_len = len(result.content) if result.content else 0
            total_content += content_len
            print(f"  Result {i+1}: {result.title[:50]}... ({content_len} chars)")
        
        print(f"✅ Total extracted content: {total_content} characters")
        print(f"✅ Web scraping working: {total_content > 1000}")
        
        return total_content > 1000
        
    except Exception as e:
        print(f"❌ Web content extraction failed: {e}")
        return False

def test_multi_agent_system():
    """Test multi-agent system"""
    print("\n🤖 Testing Multi-Agent System...")
    
    try:
        from enhanced_rag_system import MultiAgentRetriever
        
        agent_retriever = MultiAgentRetriever()
        
        # Test agent selection
        test_queries = [
            "What fertilizers work best for corn?",
            "How to manage soil pH?", 
            "Pest control for tomatoes",
            "Sustainable farming practices"
        ]
        
        for query in test_queries:
            enhancements = agent_retriever.retrieve_with_agents(query, [query])
            if enhancements:
                enhancement = enhancements[0]
                print(f"  Query: {query}")
                print(f"  Agent: {enhancement['agent']}")
                print(f"  Enhanced: {enhancement['enhanced_query'][:100]}...")
        
        print("✅ Multi-agent system working")
        return True
        
    except Exception as e:
        print(f"❌ Multi-agent system failed: {e}")
        return False

def test_system_imports():
    """Test all system imports"""
    print("\n📦 Testing System Imports...")
    
    try:
        from enhanced_rag_system import (
            EnhancedRAGSystem,
            WebSearcher, 
            MultiAgentRetriever,
            QueryRefiner,
            SubQueryGenerator,
            DatabaseRetriever,
            MarkdownGenerator,
            AnswerSynthesizer
        )
        print("✅ All core modules imported successfully")
        
        # Test package availability
        import requests
        print("✅ requests package available")
        
        from bs4 import BeautifulSoup
        print("✅ beautifulsoup4 package available")
        
        from ddgs import DDGS
        print("✅ ddgs package available")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_web_ui_status():
    """Test if web UI can check system status"""
    print("\n🌐 Testing Web UI System Status...")
    
    try:
        import sys
        sys.path.append('agri_bot_searcher/src')
        
        # Test enhanced web UI imports
        from enhanced_web_ui import app
        
        # Test system status function
        with app.test_client() as client:
            response = client.get('/api/system-status')
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ System status endpoint working")
                print(f"  Enhanced RAG: {data.get('enhanced_rag_available', False)}")
                print(f"  Legacy Chatbot: {data.get('legacy_chatbot_available', False)}")
                print(f"  Mode: {data.get('mode', 'unknown')}")
                return True
            else:
                print(f"❌ System status failed: {response.status_code}")
                return False
        
    except Exception as e:
        print(f"❌ Web UI status test failed: {e}")
        return False

def main():
    """Run all quick tests"""
    print("🚀 Enhanced RAG System - Quick Test Suite")
    print("=" * 60)
    
    tests = [
        ("System Imports", test_system_imports),
        ("Web Content Extraction", test_web_content_extraction),
        ("Multi-Agent System", test_multi_agent_system),
        ("Web UI Status", test_web_ui_status)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("📊 QUICK TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print(f"\n🎉 ALL QUICK TESTS PASSED!")
        print("\nKey Features Verified:")
        print("✅ Web content extraction with BeautifulSoup")
        print("✅ Multi-agent system for enhanced retrieval")
        print("✅ All packages (ddgs, requests, bs4) available")
        print("✅ Web UI system status working")
        print("\n🚀 System is ready for full testing!")
        print("\nTo start the web UI:")
        print("  cd /store/Answering_Agriculture")
        print("  ./start_agri_bot.sh")
    else:
        print(f"\n⚠️  Some quick tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
