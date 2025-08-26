#!/usr/bin/env python3
"""
Test script for IndicAgri Voice Integration

This script tests the voice transcription capabilities and basic functionality
of the IndicAgri Bot integration.
"""

import sys
import os
from pathlib import Path

# Add paths for testing
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / 'agri_bot_searcher' / 'src'))
sys.path.insert(0, str(current_dir / 'agri_bot'))

def test_basic_imports():
    """Test if basic modules can be imported"""
    print("Testing basic imports...")
    
    try:
        from indicagri_voice_integration import IndicAgriVoiceTranscriber, get_supported_languages
        print("✓ IndicAgri voice integration module imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import IndicAgri voice module: {e}")
        return False

def test_voice_transcriber():
    """Test voice transcriber initialization"""
    print("\nTesting voice transcriber initialization...")
    
    try:
        from indicagri_voice_integration import IndicAgriVoiceTranscriber
        
        transcriber = IndicAgriVoiceTranscriber()
        print(f"✓ Voice transcriber initialized")
        print(f"  - Available: {transcriber.is_available()}")
        
        # Test language support
        languages = transcriber.get_supported_languages()
        print(f"  - Supported languages: {len(languages)}")
        print(f"  - Sample languages: {list(languages.keys())[:5]}")
        
        return True
    except Exception as e:
        print(f"✗ Voice transcriber test failed: {e}")
        return False

def test_agriculture_chatbot():
    """Test agriculture chatbot import"""
    print("\nTesting agriculture chatbot...")
    
    try:
        from agriculture_chatbot import AgricultureChatbot
        
        # Test basic initialization (without actually creating instances)
        print("✓ AgricultureChatbot imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import AgricultureChatbot: {e}")
        return False

def test_flask_app():
    """Test Flask app import"""
    print("\nTesting Flask app...")
    
    try:
        from enhanced_voice_web_ui import app, HAS_FLASK
        
        if HAS_FLASK:
            print("✓ Flask app imported successfully")
            print(f"  - App name: {app.name}")
            return True
        else:
            print("✗ Flask not available")
            return False
    except ImportError as e:
        print(f"✗ Failed to import Flask app: {e}")
        return False

def test_agri_bot_modules():
    """Test agri_bot modules"""
    print("\nTesting agri_bot modules...")
    
    try:
        from new_bot import main as transcribe_audio
        from utility import mono_channel, speech_to_text_bharat, translate_indic
        from load import ai_bharat, load_indic_trans
        
        print("✓ agri_bot modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import agri_bot modules: {e}")
        print("  Note: This is expected if agri_bot dependencies are not installed")
        return False

def test_file_structure():
    """Test if required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        'agri_bot_searcher/src/enhanced_voice_web_ui.py',
        'agri_bot_searcher/src/indicagri_voice_integration.py',
        'agri_bot_searcher/src/agriculture_chatbot.py',
        'install_agri_bot.sh',
        'start_agri_bot.sh'
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = current_dir / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (missing)")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("🌾 IndicAgri Bot Integration Test")
    print("=" * 40)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Basic Imports", test_basic_imports),
        ("Voice Transcriber", test_voice_transcriber),
        ("Agriculture Chatbot", test_agriculture_chatbot),
        ("Flask App", test_flask_app),
        ("agri_bot Modules", test_agri_bot_modules)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 40)
    print("Test Results Summary:")
    print("=" * 40)
    
    passed = 0
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status:8} {test_name}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! IndicAgri Bot should work correctly.")
    elif passed >= len(results) - 2:
        print("\n⚠️  Most tests passed. IndicAgri Bot should work with basic functionality.")
    else:
        print("\n❌ Multiple tests failed. Please check dependencies and installation.")
    
    print("\nTo start IndicAgri Bot:")
    print("1. Make sure you've run: ./install_agri_bot.sh")
    print("2. Run: ./start_agri_bot.sh")
    print("3. Open browser to: http://localhost:5000")

if __name__ == '__main__':
    main()
