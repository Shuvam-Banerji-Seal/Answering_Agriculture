#!/usr/bin/env python3
"""
Enhanced IndicAgri Bot - Web UI with Integrated Voice Transcription
A comprehensive Flask web interface for the agriculture chatbot with voice transcription capabilities
"""

try:
    from flask import Flask, request, jsonify, render_template_string
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
    
    app = Flask(__name__)
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
            if voice_transcriber.is_available():
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
                return "Voice transcription not available", "Voice transcription not available - agri_bot modules not found"
        except Exception as e:
            logging.error(f"Audio processing error: {e}")
            error_msg = f"Error processing audio: {str(e)}"
            return error_msg, error_msg

    # Enhanced HTML template with IndicAgri branding and voice capabilities
    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🌾 IndicAgri Bot - Voice & Text Interface</title>
        <style>
            :root {
                --primary-color: #2e7d32;
                --secondary-color: #4caf50;
                --accent-color: #81c784;
                --bg-color: #f1f8e9;
                --card-bg: #ffffff;
                --text-color: #1b5e20;
                --border-color: #c8e6c9;
                --shadow: 0 2px 8px rgba(46, 125, 50, 0.1);
                --voice-recording: #f44336;
                --voice-processing: #ff9800;
                --indicagri-orange: #ff6b35;
                --indicagri-green: #228b22;
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, var(--bg-color) 0%, #e8f5e8 100%);
                color: var(--text-color);
                line-height: 1.6;
                min-height: 100vh;
            }

            .container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }

            .header {
                text-align: center;
                margin-bottom: 30px;
                padding: 25px;
                background: linear-gradient(135deg, var(--card-bg) 0%, #f8fff8 100%);
                border-radius: 20px;
                box-shadow: var(--shadow);
                border: 2px solid var(--accent-color);
            }

            .header h1 {
                background: linear-gradient(45deg, var(--indicagri-green), var(--indicagri-orange));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-size: 3rem;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
                font-weight: bold;
            }

            .header .subtitle {
                font-size: 1.3rem;
                color: var(--primary-color);
                margin-bottom: 10px;
                font-weight: 600;
            }

            .header p {
                font-size: 1.1rem;
                color: var(--text-color);
                opacity: 0.8;
            }

            .main-content {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 25px;
                margin-bottom: 30px;
            }

            .config-panel, .voice-panel {
                background: var(--card-bg);
                padding: 30px;
                border-radius: 20px;
                box-shadow: var(--shadow);
                border: 1px solid var(--border-color);
            }

            .config-panel h3, .voice-panel h3 {
                color: var(--primary-color);
                margin-bottom: 25px;
                font-size: 1.5rem;
                border-bottom: 3px solid var(--accent-color);
                padding-bottom: 12px;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .form-group {
                margin-bottom: 25px;
            }

            .form-group label {
                display: block;
                margin-bottom: 10px;
                font-weight: 600;
                color: var(--text-color);
                font-size: 1.1rem;
            }

            .form-control {
                width: 100%;
                padding: 15px;
                border: 2px solid var(--border-color);
                border-radius: 10px;
                font-size: 1rem;
                transition: all 0.3s ease;
                background: #fafafa;
            }

            .form-control:focus {
                outline: none;
                border-color: var(--primary-color);
                box-shadow: 0 0 0 3px rgba(46, 125, 50, 0.1);
            }

            .language-selector {
                background: linear-gradient(135deg, #f8fff8 0%, var(--bg-color) 100%);
                border: 2px solid var(--accent-color) !important;
                padding: 12px;
                border-radius: 10px;
                font-size: 1rem;
            }

            .voice-controls {
                display: flex;
                flex-direction: column;
                gap: 20px;
                align-items: center;
            }

            .record-button {
                width: 150px;
                height: 150px;
                border-radius: 50%;
                border: none;
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                font-size: 1.2rem;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 8px 20px rgba(46, 125, 50, 0.3);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }

            .record-button:hover {
                transform: translateY(-3px);
                box-shadow: 0 12px 25px rgba(46, 125, 50, 0.4);
            }

            .record-button.recording {
                background: linear-gradient(135deg, var(--voice-recording), #d32f2f);
                animation: pulse 1.5s infinite;
            }

            .record-button.processing {
                background: linear-gradient(135deg, var(--voice-processing), #f57c00);
                animation: spin 2s linear infinite;
            }

            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .transcription-display {
                background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
                border: 2px solid var(--accent-color);
                border-radius: 15px;
                padding: 20px;
                margin-top: 20px;
                min-height: 120px;
            }

            .transcription-display h4 {
                color: var(--primary-color);
                margin-bottom: 15px;
                border-bottom: 2px solid var(--accent-color);
                padding-bottom: 8px;
            }

            .transcribed-text {
                background: white;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 15px;
                border-left: 4px solid var(--primary-color);
                font-style: italic;
                min-height: 40px;
            }

            .query-section {
                background: var(--card-bg);
                padding: 30px;
                border-radius: 20px;
                box-shadow: var(--shadow);
                border: 1px solid var(--border-color);
                margin-bottom: 30px;
            }

            .query-section h3 {
                color: var(--primary-color);
                margin-bottom: 20px;
                font-size: 1.5rem;
                border-bottom: 3px solid var(--accent-color);
                padding-bottom: 10px;
            }

            .query-input-group {
                display: flex;
                gap: 15px;
                margin-bottom: 20px;
            }

            .query-input {
                flex: 1;
                padding: 15px;
                border: 2px solid var(--border-color);
                border-radius: 10px;
                font-size: 1rem;
                resize: vertical;
                min-height: 60px;
            }

            .send-button {
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 10px;
                font-size: 1rem;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                height: fit-content;
            }

            .send-button:hover {
                background: linear-gradient(135deg, var(--secondary-color), var(--primary-color));
                transform: translateY(-2px);
                box-shadow: 0 6px 15px rgba(46, 125, 50, 0.3);
            }

            .send-button:disabled {
                background: #cccccc;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }

            .response-section {
                background: var(--card-bg);
                padding: 30px;
                border-radius: 20px;
                box-shadow: var(--shadow);
                border: 1px solid var(--border-color);
            }

            .response-section h3 {
                color: var(--primary-color);
                margin-bottom: 20px;
                font-size: 1.5rem;
                border-bottom: 3px solid var(--accent-color);
                padding-bottom: 10px;
            }

            .loading {
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 40px;
                font-size: 1.1rem;
                color: var(--primary-color);
            }

            .spinner {
                border: 3px solid var(--border-color);
                border-top: 3px solid var(--primary-color);
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                margin-right: 15px;
            }

            .response-content {
                background: linear-gradient(135deg, #f8fff8 0%, #f1f8e9 100%);
                border: 2px solid var(--accent-color);
                border-radius: 15px;
                padding: 25px;
                line-height: 1.8;
                font-size: 1.05rem;
            }

            .status-indicator {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 0.9rem;
                font-weight: 600;
                margin-top: 10px;
            }

            .status-ready {
                background: #e8f5e9;
                color: var(--primary-color);
                border: 1px solid var(--accent-color);
            }

            .status-recording {
                background: #ffebee;
                color: var(--voice-recording);
                border: 1px solid #ffcdd2;
            }

            .status-processing {
                background: #fff3e0;
                color: var(--voice-processing);
                border: 1px solid #ffcc02;
            }

            .voice-settings {
                background: linear-gradient(135deg, #f8fff8 0%, #e8f5e9 100%);
                border: 2px solid var(--accent-color);
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
            }

            .voice-settings h4 {
                color: var(--primary-color);
                margin-bottom: 15px;
                font-size: 1.2rem;
            }

            .settings-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
            }

            .checkbox-group {
                display: flex;
                align-items: center;
                gap: 10px;
                margin-top: 10px;
            }

            .checkbox-group input[type="checkbox"] {
                width: 18px;
                height: 18px;
                accent-color: var(--primary-color);
            }

            @media (max-width: 768px) {
                .main-content {
                    grid-template-columns: 1fr;
                }
                
                .query-input-group {
                    flex-direction: column;
                }
                
                .settings-grid {
                    grid-template-columns: 1fr;
                }
                
                .header h1 {
                    font-size: 2.5rem;
                }
                
                .record-button {
                    width: 120px;
                    height: 120px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌾 IndicAgri Bot</h1>
                <div class="subtitle">Advanced Agriculture Assistant with Voice Support</div>
                <p>Voice-enabled agricultural guidance for Indian farmers in multiple regional languages</p>
            </div>

            <div class="main-content">
                <div class="config-panel">
                    <h3>⚙️ Configuration</h3>
                    <div class="form-group">
                        <label for="num-agents">Number of Search Agents:</label>
                        <input type="range" id="num-agents" class="form-control" min="1" max="5" value="2">
                        <div style="text-align: center; margin-top: 5px;">
                            <span id="num-agents-value">2</span>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="ollama-port">Ollama Base Port:</label>
                        <input type="number" id="ollama-port" class="form-control" value="11434" min="1024" max="65535">
                    </div>
                </div>

                <div class="voice-panel">
                    <h3>🎤 Voice Input</h3>
                    
                    <div class="voice-settings">
                        <h4>Voice Settings</h4>
                        <div class="form-group">
                            <label for="language-select">Select Language:</label>
                            <select id="language-select" class="form-control language-selector">
                                {% for code, info in languages.items() %}
                                <option value="{{ code }}" {% if code == 'hin_Deva' %}selected{% endif %}>
                                    {{ info.name }}
                                </option>
                                {% endfor %}
                            </select>
                        </div>
                        
                        <div class="settings-grid">
                            <div class="form-group">
                                <label for="api-key">SarvamAI API Key (Optional):</label>
                                <input type="password" id="api-key" class="form-control" placeholder="Enter API key for SarvamAI">
                            </div>
                            <div class="form-group">
                                <label for="hf-token">Hugging Face Token (Optional):</label>
                                <input type="password" id="hf-token" class="form-control" placeholder="Enter HF token">
                            </div>
                        </div>
                        
                        <div class="checkbox-group">
                            <input type="checkbox" id="use-local-model" checked>
                            <label for="use-local-model">Use Local Model (uncheck for SarvamAI)</label>
                        </div>
                    </div>

                    <div class="voice-controls">
                        <button id="record-button" class="record-button">
                            <span id="record-icon">🎤</span>
                            <span id="record-text">Start Recording</span>
                        </button>
                        <div id="recording-status" class="status-indicator status-ready">
                            <span>🟢</span> Ready to Record
                        </div>
                    </div>

                    <div class="transcription-display">
                        <h4>📝 Transcription Results</h4>
                        <div id="original-text" class="transcribed-text">
                            <strong>Original:</strong> <span id="original-content">No transcription yet</span>
                        </div>
                        <div id="translated-text" class="transcribed-text">
                            <strong>English:</strong> <span id="translated-content">No translation yet</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="query-section">
                <h3>💬 Ask Your Question</h3>
                <div class="query-input-group">
                    <textarea id="query-input" class="query-input" placeholder="Type your agricultural question here or use voice input above..."></textarea>
                    <button id="send-button" class="send-button">Send Query</button>
                </div>
            </div>

            <div class="response-section">
                <h3>🌱 IndicAgri Response</h3>
                <div id="response-content" class="response-content">
                    Welcome to IndicAgri Bot! Ask any agriculture-related question in text or voice.
                </div>
            </div>
        </div>

        <script>
            // Global variables
            let mediaRecorder;
            let audioChunks = [];
            let isRecording = false;
            let isProcessing = false;

            // DOM elements
            const recordButton = document.getElementById('record-button');
            const recordIcon = document.getElementById('record-icon');
            const recordText = document.getElementById('record-text');
            const recordingStatus = document.getElementById('recording-status');
            const queryInput = document.getElementById('query-input');
            const sendButton = document.getElementById('send-button');
            const responseContent = document.getElementById('response-content');
            const numAgentsSlider = document.getElementById('num-agents');
            const numAgentsValue = document.getElementById('num-agents-value');
            const originalContent = document.getElementById('original-content');
            const translatedContent = document.getElementById('translated-content');

            // Update agent count display
            numAgentsSlider.addEventListener('input', function() {
                numAgentsValue.textContent = this.value;
            });

            // Initialize voice recording
            async function initializeVoiceRecording() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ 
                        audio: {
                            sampleRate: 16000,
                            channelCount: 1,
                            echoCancellation: true,
                            noiseSuppression: true
                        } 
                    });
                    
                    mediaRecorder = new MediaRecorder(stream);
                    
                    mediaRecorder.ondataavailable = event => {
                        audioChunks.push(event.data);
                    };
                    
                    mediaRecorder.onstop = async () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        audioChunks = [];
                        await processAudio(audioBlob);
                    };
                    
                } catch (error) {
                    console.error('Error initializing voice recording:', error);
                    alert('Error accessing microphone. Please check permissions.');
                }
            }

            // Record button click handler
            recordButton.addEventListener('click', async function() {
                if (!mediaRecorder) {
                    await initializeVoiceRecording();
                }
                
                if (!isRecording && !isProcessing) {
                    startRecording();
                } else if (isRecording) {
                    stopRecording();
                }
            });

            function startRecording() {
                isRecording = true;
                recordButton.classList.add('recording');
                recordIcon.textContent = '⏹️';
                recordText.textContent = 'Stop Recording';
                recordingStatus.innerHTML = '<span>🔴</span> Recording...';
                recordingStatus.className = 'status-indicator status-recording';
                
                audioChunks = [];
                mediaRecorder.start();
            }

            function stopRecording() {
                isRecording = false;
                isProcessing = true;
                recordButton.classList.remove('recording');
                recordButton.classList.add('processing');
                recordIcon.textContent = '⏳';
                recordText.textContent = 'Processing...';
                recordingStatus.innerHTML = '<span>🟡</span> Processing Audio...';
                recordingStatus.className = 'status-indicator status-processing';
                
                mediaRecorder.stop();
            }

            async function processAudio(audioBlob) {
                try {
                    const formData = new FormData();
                    formData.append('audio', audioBlob, 'recording.wav');
                    formData.append('language', document.getElementById('language-select').value);
                    formData.append('use_local_model', document.getElementById('use-local-model').checked);
                    formData.append('api_key', document.getElementById('api-key').value);
                    formData.append('hf_token', document.getElementById('hf-token').value);

                    const response = await fetch('/transcribe', {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();
                    
                    if (result.success) {
                        originalContent.textContent = result.original || 'No original text';
                        translatedContent.textContent = result.english || 'No translation';
                        
                        // Auto-fill the query input with English translation
                        if (result.english) {
                            queryInput.value = result.english;
                        }
                        
                        showSuccess('Voice transcription completed successfully!');
                    } else {
                        showError('Transcription failed: ' + (result.error || 'Unknown error'));
                    }
                } catch (error) {
                    console.error('Error processing audio:', error);
                    showError('Error processing audio: ' + error.message);
                } finally {
                    resetRecordingState();
                }
            }

            function resetRecordingState() {
                isRecording = false;
                isProcessing = false;
                recordButton.classList.remove('recording', 'processing');
                recordIcon.textContent = '🎤';
                recordText.textContent = 'Start Recording';
                recordingStatus.innerHTML = '<span>🟢</span> Ready to Record';
                recordingStatus.className = 'status-indicator status-ready';
            }

            // Send query
            sendButton.addEventListener('click', async function() {
                const query = queryInput.value.trim();
                if (!query) {
                    showError('Please enter a question or record voice input');
                    return;
                }

                sendButton.disabled = true;
                sendButton.textContent = 'Processing...';
                responseContent.innerHTML = '<div class="loading"><div class="spinner"></div>Getting response from IndicAgri Bot...</div>';

                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            query: query,
                            num_agents: parseInt(numAgentsSlider.value),
                            base_port: parseInt(document.getElementById('ollama-port').value)
                        })
                    });

                    const result = await response.json();
                    
                    if (result.success) {
                        responseContent.innerHTML = result.response;
                    } else {
                        responseContent.innerHTML = '<div style="color: var(--voice-recording);">Error: ' + (result.error || 'Unknown error occurred') + '</div>';
                    }
                } catch (error) {
                    console.error('Error sending query:', error);
                    responseContent.innerHTML = '<div style="color: var(--voice-recording);">Error: ' + error.message + '</div>';
                } finally {
                    sendButton.disabled = false;
                    sendButton.textContent = 'Send Query';
                }
            });

            // Helper functions
            function showSuccess(message) {
                console.log('Success:', message);
                // You can implement a toast notification here
            }

            function showError(message) {
                console.error('Error:', message);
                alert(message); // Simple alert for now
            }

            // Allow Enter key to send query (Ctrl+Enter for new line)
            queryInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.ctrlKey) {
                    e.preventDefault();
                    sendButton.click();
                }
            });

            // Initialize on page load
            document.addEventListener('DOMContentLoaded', function() {
                console.log('IndicAgri Bot initialized');
            });
        </script>
    </body>
    </html>
    """

    @app.route('/')
    def index():
        """Render the main interface"""
        return render_template_string(HTML_TEMPLATE, languages=LANGUAGE_MAPPINGS)

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

    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'voice_transcription_available': voice_transcriber.is_available(),
            'timestamp': datetime.now().isoformat()
        })

    def run_server(host='0.0.0.0', port=5000, debug=False):
        """Run the Flask server"""
        if not HAS_FLASK:
            print("Flask not available. Please install with: pip install flask flask-cors")
            return
            
        print(f"🌾 Starting IndicAgri Bot Web Interface on http://{host}:{port}")
        print(f"Voice transcription: {'✓ Available' if voice_transcriber.is_available() else '✗ Not available'}")
        
        app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='IndicAgri Bot - Enhanced Voice & Text Interface')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    if HAS_FLASK:
        run_server(host=args.host, port=args.port, debug=args.debug)
    else:
        print("Flask not available. Please install requirements first.")
