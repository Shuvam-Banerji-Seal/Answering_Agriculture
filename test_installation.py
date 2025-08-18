#!/usr/bin/env python3
"""
Quick test script to verify Agriculture Bot installation
This script tests core functionality after installation
"""

import sys
import os
import subprocess
import requests
import time
from pathlib import Path

def test_imports():
    """Test critical Python imports"""
    print("🔍 Testing Python imports...")
    
    try:
        import torch
        print("✅ PyTorch imported successfully")
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")
        return False
    
    try:
        from duckduckgo_search import DDGS
        print("✅ DuckDuckGo Search imported successfully")
    except ImportError as e:
        print(f"❌ DuckDuckGo Search import failed: {e}")
        return False
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    return True

def test_ollama():
    """Test Ollama service and model"""
    print("\n🤖 Testing Ollama service...")
    
    # Check if ollama command exists
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed")
        else:
            print("❌ Ollama not found")
            return False
    except FileNotFoundError:
        print("❌ Ollama command not found")
        return False
    
    # Check if service is running
    try:
        response = requests.get('http://localhost:11434/api/version', timeout=5)
        if response.status_code == 200:
            print("✅ Ollama service is running")
        else:
            print("❌ Ollama service not responding")
            return False
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to Ollama service")
        return False
    
    # Check if gemma3:1b model is available
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if 'gemma3:1b' in result.stdout:
            print("✅ gemma3:1b model is available")
        else:
            print("❌ gemma3:1b model not found")
            return False
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return False
    
    return True

def test_agriculture_bot():
    """Test agriculture bot modules"""
    print("\n🌾 Testing Agriculture Bot modules...")
    
    # Add src directory to path
    project_root = Path(__file__).parent
    src_path = project_root / "agri_bot_searcher" / "src"
    
    if not src_path.exists():
        print(f"❌ Source directory not found: {src_path}")
        return False
    
    sys.path.insert(0, str(src_path))
    
    try:
        from agriculture_chatbot import AgricultureChatbot
        print("✅ Agriculture Chatbot module imported")
    except ImportError as e:
        print(f"❌ Agriculture Chatbot import failed: {e}")
        return False
    
    try:
        from web_ui import app
        print("✅ Web UI module imported")
    except ImportError as e:
        print(f"❌ Web UI import failed: {e}")
        return False
    
    return True

def test_quick_query():
    """Test a quick query to ensure the system works end-to-end"""
    print("\n🔬 Testing quick query...")
    
    try:
        # Add src to path
        project_root = Path(__file__).parent
        src_path = project_root / "agri_bot_searcher" / "src"
        sys.path.insert(0, str(src_path))
        
        from agriculture_chatbot import AgricultureChatbot
        
        # Create chatbot instance
        chatbot = AgricultureChatbot()
        
        # Test simple query
        result = chatbot.process_query("What is organic farming?")
        
        if result and len(result) > 10:
            print("✅ Quick query test passed")
            print(f"   Response length: {len(result)} characters")
            return True
        else:
            print("❌ Quick query test failed - no meaningful response")
            return False
            
    except Exception as e:
        print(f"❌ Quick query test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Agriculture Bot Installation Test")
    print("=" * 50)
    
    tests = [
        ("Python Imports", test_imports),
        ("Ollama Service", test_ollama),
        ("Agriculture Bot", test_agriculture_bot),
        ("Quick Query", test_quick_query)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test ERROR: {e}")
    
    print(f"\n📊 Test Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Agriculture Bot is ready to use.")
        print("\n🚀 To start the application:")
        print("   ./start_agri_bot.sh")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the installation.")
        print("\n🔧 To reinstall:")
        print("   ./install_agri_bot.sh")
        return 1

if __name__ == "__main__":
    sys.exit(main())
