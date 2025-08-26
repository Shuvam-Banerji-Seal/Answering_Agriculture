#!/usr/bin/env python3
"""
Enhanced IndicAgri Bot - Simplified Web UI with Static Files
A comprehensive Flask web interface for the agriculture chatbot with voice transcription capabilities
"""

try:
    from flask import Flask, request, jsonify, send_from_directory, render_template
    from flask_cors import CORS
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

import sys
import os
import json
import logging
import time
import tempfile
import base64
import subprocess
from datetime import datetime
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

if HAS_FLASK:
    from agriculture_chatbot import AgricultureChatbot
    from indicagri_voice_integration import IndicAgriVoiceTranscriber, get_supported_languages
    
    # Initialize voice transcriber
    voice_transcriber = IndicAgriVoiceTranscriber()
    
    app = Flask(__name__, static_folder='static', template_folder='static')
    CORS(app)  # Enable CORS for all domains
    
    # Initialize chatbot
    chatbot = None
    
    # Language mappings for IndicAgri
    LANGUAGE_MAPPINGS = get_supported_languages()
    
    def get_chatbot_instance(base_port=11434, num_agents=2):
        """Get or create chatbot instance with specified parameters"""
        global chatbot
        if chatbot is None or chatbot.base_port != base_port or chatbot.num_agents != num_agents:
            chatbot = AgricultureChatbot(base_port=base_port, num_agents=num_agents)
        return chatbot
    
    def process_audio_file(audio_path, language_code, use_local_model=True, api_key=None, hf_token=None):
        """Process audio file using IndicAgri voice transcription"""
        try:
            if voice_transcriber.is_available() or api_key:
                # Use the integrated IndicAgri voice transcription
                original_text, english_text = voice_transcriber.transcribe_audio(
                    audio_path=audio_path,
                    language_code=language_code,
                    use_local_model=use_local_model,
                    api_key=api_key,
                    hf_token=hf_token
                )
                return original_text, english_text
            else:
                error_msg = "Voice transcription requires SarvamAI API key. Please enter your API key in the settings."
                return error_msg, error_msg
        except Exception as e:
            logging.error(f"Audio processing error: {e}")
            error_msg = f"Error processing audio: {str(e)}"
            return error_msg, error_msg

    @app.route('/')
    def index():
        """Serve the main HTML file"""
        return send_from_directory('static', 'index.html')

    @app.route('/static/<path:filename>')
    def serve_static(filename):
        """Serve static files"""
        return send_from_directory('static', filename)

    @app.route('/transcribe', methods=['POST'])
    def transcribe():
        """Handle voice transcription requests"""
        try:
            if 'audio' not in request.files:
                return jsonify({'success': False, 'error': 'No audio file provided'})
            
            audio_file = request.files['audio']
            language_code = request.form.get('language', 'hin_Deva')
            use_local_model = request.form.get('use_local_model', 'true').lower() == 'true'
            api_key = request.form.get('api_key', '')
            hf_token = request.form.get('hf_token', '')
            
            # Save uploaded audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                audio_file.save(tmp_file.name)
                temp_audio_path = tmp_file.name
            
            try:
                # Process audio using IndicAgri voice transcription
                original_text, english_text = process_audio_file(
                    audio_path=temp_audio_path,
                    language_code=language_code,
                    use_local_model=use_local_model,
                    api_key=api_key if api_key else None,
                    hf_token=hf_token if hf_token else None
                )
                
                return jsonify({
                    'success': True,
                    'original': original_text,
                    'english': english_text
                })
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_audio_path)
                except OSError:
                    pass
                    
        except Exception as e:
            logging.error(f"Transcription error: {e}")
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/chat', methods=['POST'])
    def chat():
        """Handle chat requests"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No JSON data provided'})
                
            query = data.get('query', '').strip()
            num_agents = data.get('num_agents', 2)
            base_port = data.get('base_port', 11434)
            
            if not query:
                return jsonify({'success': False, 'error': 'No query provided'})
            
            # Get chatbot instance
            bot = get_chatbot_instance(base_port=base_port, num_agents=num_agents)
            
            # Process the query - use the correct method name
            if hasattr(bot, 'answer_query'):
                result = bot.answer_query(query)
                response = result.get('answer', str(result))
            else:
                # Fallback method
                response = f"Query processed: {query}. IndicAgri Bot response would appear here."
            
            return jsonify({'success': True, 'response': response})
            
        except Exception as e:
            logging.error(f"Chat error: {e}")
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'voice_available': voice_transcriber.is_available(),
            'timestamp': datetime.now().isoformat()
        })

    def run_app():
        """Run the Flask application"""
        print("🌾 Starting IndicAgri Bot Web Interface on http://0.0.0.0:5000")
        print(f"Voice transcription: {'✓ Available' if voice_transcriber.is_available() else '✗ Requires API key'}")
        
        try:
            app.run(host='0.0.0.0', port=5000, debug=False)
        except Exception as e:
            print(f"Error starting Flask app: {e}")
            return False
        return True

if __name__ == '__main__':
    if not HAS_FLASK:
        print("Error: Flask not available. Please install flask and flask-cors")
        print("pip install flask flask-cors")
        sys.exit(1)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    run_app()
else:
    # This allows the app to be imported and run from other modules
    if HAS_FLASK:
        def main():
            return run_app()
    else:
        def main():
            print("Error: Flask not available")
            return False
