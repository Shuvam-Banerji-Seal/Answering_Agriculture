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

            .status-warning {
                background: #fff8e1;
                color: #f57c00;
                border: 1px solid #ffcc02;
            }

            .status-error {
                background: #ffebee;
                color: var(--voice-recording);
                border: 1px solid #ffcdd2;
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
                <div id="mic-help" style="background: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; margin-top: 10px; border: 1px solid #ffeaa7; display: none;">
                    <strong>📢 Microphone Issues?</strong><br>
                    • Click the 🔒 icon in your browser's address bar<br>
                    • Select "Allow" for microphone permissions<br>
                    • Refresh the page and try again<br>
                    • Or use <strong>http://localhost:5000</strong> instead
                </div>
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
                                <small class="text-muted">
                                    <a href="#" onclick="showApiKeyHelp('sarvam')" style="color: var(--primary-color);">
                                        ℹ️ How to get SarvamAI API Key?
                                    </a>
                                </small>
                            </div>
                            <div class="form-group">
                                <label for="hf-token">Hugging Face Token (Optional):</label>
                                <input type="password" id="hf-token" class="form-control" placeholder="Enter HF token">
                                <small class="text-muted">
                                    <a href="#" onclick="showApiKeyHelp('huggingface')" style="color: var(--primary-color);">
                                        ℹ️ How to get Hugging Face Token?
                                    </a>
                                </small>
                            </div>
                        </div>
                        
                        <div class="checkbox-group">
                            <input type="checkbox" id="use-local-model">
                            <label for="use-local-model">Use Local Model (experimental - requires setup)</label>
                            <small class="text-muted" style="display: block; margin-top: 5px;">
                                ⚠️ Local models currently disabled due to dependency conflicts. SarvamAI recommended.
                            </small>
                        </div>

                        <div class="info-box" style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 5px; margin-top: 15px;">
                            <small style="color: #856404;">
                                🔒 <strong>Security Note:</strong> API keys are stored locally in your browser and transmitted securely. 
                                For production use, consider accessing via HTTPS. On localhost, HTTP is acceptable for development.
                            </small>
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

            // Initialize voice recording with better browser compatibility
            async function initializeVoiceRecording() {
                try {
                    // Check browser support using multiple methods (following Stack Overflow best practices)
                    let getUserMedia = null;
                    
                    // Modern browsers
                    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                        getUserMedia = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
                    } 
                    // Older browsers with prefixes
                    else if (navigator.getUserMedia) {
                        getUserMedia = navigator.getUserMedia.bind(navigator);
                    } 
                    else if (navigator.webkitGetUserMedia) {
                        getUserMedia = navigator.webkitGetUserMedia.bind(navigator);
                    } 
                    else if (navigator.mozGetUserMedia) {
                        getUserMedia = navigator.mozGetUserMedia.bind(navigator);
                    }
                    
                    if (!getUserMedia) {
                        throw new Error('Browser does not support microphone access. Please use Chrome 53+, Firefox 36+, or Safari 11+.');
                    }

                    // Check secure context
                    const isSecureContext = window.isSecureContext || location.protocol === 'https:' || 
                                          location.hostname === 'localhost' || location.hostname === '127.0.0.1';
                    
                    if (!isSecureContext) {
                        throw new Error('Microphone access requires HTTPS or localhost. Please access via https:// or localhost.');
                    }

                    // Show permission request status
                    recordingStatus.innerHTML = '<span>Requesting microphone access...</span>';
                    recordingStatus.className = 'status-indicator status-warning';

                    // Request microphone access with fallback for older browsers
                    let stream;
                    const constraints = { 
                        audio: {
                            echoCancellation: true,
                            noiseSuppression: true,
                            autoGainControl: true,
                            sampleRate: 16000,
                            channelCount: 1
                        } 
                    };

                    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                        // Modern promise-based approach
                        stream = await navigator.mediaDevices.getUserMedia(constraints);
                    } else {
                        // Legacy callback-based approach
                        stream = await new Promise((resolve, reject) => {
                            getUserMedia(constraints, resolve, reject);
                        });
                    }
                    
                    // Check MediaRecorder support
                    if (!window.MediaRecorder) {
                        throw new Error('MediaRecorder not supported. Please use Chrome 47+, Firefox 25+, or Safari 14+.');
                    }

                    // Determine best MIME type
                    let mimeType = '';
                    const supportedTypes = [
                        'audio/webm;codecs=opus',
                        'audio/webm',
                        'audio/mp4',
                        'audio/wav'
                    ];
                    
                    for (const type of supportedTypes) {
                        if (MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(type)) {
                            mimeType = type;
                            break;
                        }
                    }
                    
                    mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : {});
                    
                    mediaRecorder.ondataavailable = event => {
                        if (event.data.size > 0) {
                            audioChunks.push(event.data);
                        }
                    };
                    
                    mediaRecorder.onstop = async () => {
                        // Stop all tracks to release microphone
                        stream.getTracks().forEach(track => track.stop());
                        
                        const audioBlob = new Blob(audioChunks, { type: mimeType || 'audio/wav' });
                        audioChunks = [];
                        await processAudio(audioBlob);
                    };

                    mediaRecorder.onerror = function(event) {
                        console.error('MediaRecorder error:', event.error);
                        showError('Recording error: ' + event.error.message);
                        resetRecordingState();
                    };

                    // Success - update status
                    recordingStatus.innerHTML = '<span>Ready to Record</span>';
                    recordingStatus.className = 'status-indicator status-ready';
                    showSuccess('Microphone access granted. Ready to record!');
                    
                } catch (error) {
                    console.error('Error initializing voice recording:', error);
                    let errorMessage = 'Microphone access failed: ';
                    
                    if (error.name === 'NotAllowedError') {
                        errorMessage += 'Permission denied. Please allow microphone access in your browser and refresh the page.';
                    } else if (error.name === 'NotFoundError') {
                        errorMessage += 'No microphone found. Please connect a microphone and try again.';
                    } else if (error.name === 'NotSupportedError') {
                        errorMessage += 'Microphone not supported by your browser. Please use Chrome 53+, Firefox 36+, or Safari 11+.';
                    } else if (error.name === 'SecurityError') {
                        errorMessage += 'Security error. Please access via HTTPS or localhost.';
                    } else if (error.message.includes('HTTPS') || error.message.includes('localhost')) {
                        errorMessage += error.message;
                    } else {
                        errorMessage += error.message || 'Unknown error occurred.';
                    }
                    
                    // Add helpful suggestions without problematic escaping
                    errorMessage += ' Troubleshooting: Make sure you are using HTTPS or localhost, check browser permissions for microphone, try refreshing the page, use Chrome, Firefox, or Safari latest version.';
                    
                    showError(errorMessage);
                    recordingStatus.innerHTML = '<span>Microphone unavailable</span>';
                    recordingStatus.className = 'status-indicator status-error';
                }
            }

            // Record button click handler
            recordButton.addEventListener('click', async function() {
                if (!mediaRecorder) {
                    await initializeVoiceRecording();
                    // If initialization still failed, don't proceed
                    if (!mediaRecorder) {
                        showError('Voice recording initialization failed. Please check the troubleshooting steps above.');
                        return;
                    }
                }
                
                if (!isRecording && !isProcessing) {
                    startRecording();
                } else if (isRecording) {
                    stopRecording();
                }
                }
            });

            function startRecording() {
                if (!mediaRecorder) {
                    showError('Microphone not initialized. Please check browser compatibility and try again.');
                    return;
                }
                
                isRecording = true;
                recordButton.classList.add('recording');
                recordIcon.textContent = 'Stop';
                recordText.textContent = 'Stop Recording';
                recordingStatus.innerHTML = '<span>Recording...</span>';
                recordingStatus.className = 'status-indicator status-recording';
                
                audioChunks = [];
                mediaRecorder.start();
            }

            function stopRecording() {
                if (!mediaRecorder) {
                    showError('Microphone not initialized. Cannot stop recording.');
                    resetRecordingState();
                    return;
                }
                
                isRecording = false;
                isProcessing = true;
                recordButton.classList.remove('recording');
                recordButton.classList.add('processing');
                recordIcon.textContent = 'Processing';
                recordText.textContent = 'Processing...';
                recordingStatus.innerHTML = '<span>Processing Audio...</span>';
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
                recordIcon.textContent = 'Mic';
                recordText.textContent = 'Start Recording';
                recordingStatus.innerHTML = '<span>Ready to Record</span>';
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
                alert(message);
            }

            // Allow Enter key to send query (Ctrl+Enter for new line)
            queryInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.ctrlKey) {
                    e.preventDefault();
                    sendButton.click();
                }
            });

            // API Key Help Functions
            function showApiKeyHelp(service) {
                let title, content;
                
                if (service === 'sarvam') {
                    title = "How to get SarvamAI API Key";
                    content = `
                        <div style="text-align: left;">
                            <h4>SarvamAI API Key Setup:</h4>
                            <ol>
                                <li>Visit <a href="https://www.sarvam.ai/" target="_blank">sarvam.ai</a></li>
                                <li>Click on "Sign Up" or "Login" if you already have an account</li>
                                <li>Complete the registration process</li>
                                <li>Navigate to your dashboard/API section</li>
                                <li>Generate a new API key</li>
                                <li>Copy the API key and paste it in the field above</li>
                            </ol>
                            <p><strong>Note:</strong> SarvamAI provides excellent voice transcription for Indian languages
                            with high accuracy and no local setup required. This is the recommended approach for IndicAgri Bot.</p>
                        </div>
                    `;
                } else if (service === 'huggingface') {
                    title = "How to get Hugging Face Token";
                    content = `
                        <div style="text-align: left;">
                            <h4>Hugging Face Token Setup:</h4>
                            <ol>
                                <li>Visit <a href="https://huggingface.co/" target="_blank">huggingface.co</a></li>
                                <li>Click "Sign Up" or "Login" if you have an account</li>
                                <li>Go to your profile → Settings → Access Tokens</li>
                                <li>Click "New token"</li>
                                <li>Choose "Read" permissions (sufficient for most models)</li>
                                <li>Give your token a name (e.g., "IndicAgri Bot")</li>
                                <li>Copy the generated token and paste it above</li>
                            </ol>
                            <p><strong>Note:</strong> This token allows access to private/gated Hugging Face models. 
                            Many models work without a token.</p>
                        </div>
                    `;
                }
                
                // Create modal
                const modal = document.createElement('div');
                modal.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.5);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    z-index: 1000;
                `;
                
                const modalContent = document.createElement('div');
                modalContent.style.cssText = `
                    background: white;
                    padding: 30px;
                    border-radius: 15px;
                    max-width: 600px;
                    max-height: 80%;
                    overflow-y: auto;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                    position: relative;
                `;
                
                modalContent.innerHTML = `
                    <button onclick="this.closest('[style*=position]').remove()" 
                            style="position: absolute; top: 10px; right: 15px; background: none; 
                                   border: none; font-size: 24px; cursor: pointer; color: #666;">×</button>
                    <h3 style="color: var(--primary-color); margin-bottom: 20px;">${title}</h3>
                    ${content}
                    <div style="text-align: center; margin-top: 20px;">
                        <button onclick="this.closest('[style*=position]').remove()" 
                                style="background: var(--primary-color); color: white; border: none; 
                                       padding: 10px 20px; border-radius: 5px; cursor: pointer;">Close</button>
                    </div>
                `;
                
                modal.appendChild(modalContent);
                document.body.appendChild(modal);
                
                // Close on background click
                modal.addEventListener('click', function(e) {
                    if (e.target === modal) {
                        modal.remove();
                    }
                });
            }

            // Initialize on page load
            document.addEventListener('DOMContentLoaded', function() {
                console.log('IndicAgri Bot initialized');
                
                // Check browser compatibility first
                checkBrowserCompatibility();
                
                // Load saved API keys from localStorage
                const savedSarvamKey = localStorage.getItem('sarvam_api_key');
                const savedHfToken = localStorage.getItem('hf_token');
                
                if (savedSarvamKey) {
                    document.getElementById('api-key').value = savedSarvamKey;
                }
                if (savedHfToken) {
                    document.getElementById('hf-token').value = savedHfToken;
                }
                
                // Initialize voice recording (request microphone access on first click)
                // No automatic initialization to avoid permission prompt on page load
                
                // Save API keys when they change
                document.getElementById('api-key').addEventListener('change', function() {
                    if (this.value) {
                        localStorage.setItem('sarvam_api_key', this.value);
                    } else {
                        localStorage.removeItem('sarvam_api_key');
                    }
                });
                
                document.getElementById('hf-token').addEventListener('change', function() {
                    if (this.value) {
                        localStorage.setItem('hf_token', this.value);
                    } else {
                        localStorage.removeItem('hf_token');
                    }
                });
            });

            function checkBrowserCompatibility() {
                const isSecureContext = window.isSecureContext || location.protocol === 'https:' || location.hostname === 'localhost' || location.hostname === '127.0.0.1';
                
                if (!isSecureContext) {
                    showWarning('WARNING: For voice features, please access via HTTPS or localhost. Current URL: ' + location.href);
                    recordingStatus.innerHTML = '<span>HTTPS required for voice</span>';
                    recordingStatus.className = 'status-indicator status-warning';
                    return;
                }

                if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                    showWarning('WARNING: Your browser does not support microphone access. Please use Chrome 53+, Firefox 36+, or Safari 11+.');
                    recordingStatus.innerHTML = '<span>Browser not supported</span>';
                    recordingStatus.className = 'status-indicator status-error';
                    return;
                }

                if (!window.MediaRecorder) {
                    showWarning('WARNING: Your browser does not support audio recording. Please use Chrome 47+, Firefox 25+, or Safari 14+.');
                    recordingStatus.innerHTML = '<span>Recording not supported</span>';
                    recordingStatus.className = 'status-indicator status-error';
                    return;
                }

                // Browser is compatible
                recordingStatus.innerHTML = '<span>Click to start recording</span>';
                recordingStatus.className = 'status-indicator status-ready';
            }

            function showWarning(message) {
                console.warn(message);
                // Create a subtle warning banner
                const warningDiv = document.createElement('div');
                warningDiv.style.cssText = `
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    color: #856404;
                    padding: 10px;
                    margin: 10px 0;
                    border-radius: 5px;
                    font-size: 14px;
                `;
                warningDiv.innerHTML = message;
                
                // Add to top of container
                const container = document.querySelector('.container');
                container.insertBefore(warningDiv, container.firstChild);
            }
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
