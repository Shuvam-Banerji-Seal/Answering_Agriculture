#!/usr/bin/env python3
"""
Enhanced Agriculture Bot Searcher - Web UI with Voice Input
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
from datetime import datetime
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

if HAS_FLASK:
    from agriculture_chatbot import AgricultureChatbot
    from voice_transcription import VoiceTranscriber, VoiceTranscriptionError

    app = Flask(__name__)
    CORS(app)  # Enable CORS for all domains

    # Initialize chatbot and transcriber
    chatbot = None
    voice_transcriber = None
    
    def get_chatbot_instance(base_port=11434, num_agents=2):
        """Get or create chatbot instance with specified parameters"""
        global chatbot
        if chatbot is None or chatbot.base_port != base_port or chatbot.num_agents != num_agents:
            chatbot = AgricultureChatbot(base_port=base_port, num_agents=num_agents)
        return chatbot
    
    def get_transcriber_instance(conformer_model_path=None):
        """Get or create voice transcriber instance"""
        global voice_transcriber
        if voice_transcriber is None:
            # Look for conformer model in audio_stuff directory
            if not conformer_model_path:
                audio_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'audio_stuff')
                potential_paths = [
                    os.path.join(audio_dir, 'conformer.nemo'),
                    os.path.join(audio_dir, 'models', 'conformer.nemo'),
                    'conformer.nemo'
                ]
                for path in potential_paths:
                    if os.path.exists(path):
                        conformer_model_path = path
                        break
            
            voice_transcriber = VoiceTranscriber(
                conformer_model_path=conformer_model_path,
                use_sarvam=True
            )
        return voice_transcriber

    # Enhanced HTML template with voice input capabilities
    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🌾 Agriculture Bot Searcher - Voice & Text Interface</title>
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
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }

            .header {
                text-align: center;
                margin-bottom: 30px;
                padding: 20px;
                background: var(--card-bg);
                border-radius: 15px;
                box-shadow: var(--shadow);
            }

            .header h1 {
                color: var(--primary-color);
                font-size: 2.5rem;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            }

            .header p {
                font-size: 1.2rem;
                color: var(--text-color);
                opacity: 0.8;
            }

            .main-content {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 30px;
            }

            .config-panel, .voice-panel {
                background: var(--card-bg);
                padding: 25px;
                border-radius: 15px;
                box-shadow: var(--shadow);
                border: 1px solid var(--border-color);
            }

            .config-panel h3, .voice-panel h3 {
                color: var(--primary-color);
                margin-bottom: 20px;
                font-size: 1.4rem;
                border-bottom: 2px solid var(--accent-color);
                padding-bottom: 10px;
            }

            .form-group {
                margin-bottom: 20px;
            }

            .form-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: var(--text-color);
            }

            .form-control {
                width: 100%;
                padding: 12px;
                border: 2px solid var(--border-color);
                border-radius: 8px;
                font-size: 1rem;
                transition: all 0.3s ease;
                background: #fafafa;
            }

            .form-control:focus {
                outline: none;
                border-color: var(--primary-color);
                box-shadow: 0 0 0 3px rgba(46, 125, 50, 0.1);
            }

            .form-control-inline {
                display: flex;
                align-items: center;
                gap: 15px;
            }

            .form-control-inline input[type="range"] {
                flex: 1;
                background: var(--accent-color);
            }

            .form-control-inline .value-display {
                background: var(--primary-color);
                color: white;
                padding: 5px 12px;
                border-radius: 20px;
                font-weight: bold;
                min-width: 40px;
                text-align: center;
            }

            .radio-group {
                display: flex;
                gap: 20px;
                flex-wrap: wrap;
            }

            .radio-option {
                display: flex;
                align-items: center;
                gap: 8px;
                background: #f5f5f5;
                padding: 10px 15px;
                border-radius: 25px;
                border: 2px solid var(--border-color);
                transition: all 0.3s ease;
                cursor: pointer;
            }

            .radio-option:hover {
                background: var(--accent-color);
                color: white;
            }

            .radio-option input[type="radio"]:checked + .radio-option {
                background: var(--primary-color);
                color: white;
                border-color: var(--primary-color);
            }

            /* Voice Input Styles */
            .voice-controls {
                display: flex;
                flex-direction: column;
                gap: 15px;
                align-items: center;
            }

            .language-selector {
                width: 100%;
            }

            .voice-button {
                width: 120px;
                height: 120px;
                border-radius: 50%;
                border: 4px solid var(--primary-color);
                background: linear-gradient(135deg, var(--secondary-color) 0%, var(--primary-color) 100%);
                color: white;
                font-size: 2rem;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
                overflow: hidden;
            }

            .voice-button:hover {
                transform: scale(1.05);
                box-shadow: 0 5px 15px rgba(46, 125, 50, 0.3);
            }

            .voice-button.recording {
                background: linear-gradient(135deg, var(--voice-recording) 0%, #d32f2f 100%);
                animation: pulse 1.5s infinite;
                border-color: var(--voice-recording);
            }

            .voice-button.processing {
                background: linear-gradient(135deg, var(--voice-processing) 0%, #f57c00 100%);
                border-color: var(--voice-processing);
            }

            @keyframes pulse {
                0% {
                    transform: scale(1);
                    box-shadow: 0 0 0 0 rgba(244, 67, 54, 0.7);
                }
                70% {
                    transform: scale(1.05);
                    box-shadow: 0 0 0 10px rgba(244, 67, 54, 0);
                }
                100% {
                    transform: scale(1);
                    box-shadow: 0 0 0 0 rgba(244, 67, 54, 0);
                }
            }

            .voice-status {
                text-align: center;
                font-weight: 600;
                padding: 10px;
                border-radius: 8px;
                margin-top: 10px;
            }

            .voice-status.idle {
                background: #e8f5e9;
                color: var(--primary-color);
            }

            .voice-status.recording {
                background: #ffebee;
                color: var(--voice-recording);
            }

            .voice-status.processing {
                background: #fff3e0;
                color: var(--voice-processing);
            }

            /* Query Panel */
            .query-panel {
                background: var(--card-bg);
                padding: 25px;
                border-radius: 15px;
                box-shadow: var(--shadow);
                border: 1px solid var(--border-color);
                margin-bottom: 20px;
            }

            .query-input {
                min-height: 120px;
                resize: vertical;
                font-family: inherit;
            }

            .btn {
                background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 25px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-top: 15px;
                width: 100%;
            }

            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(46, 125, 50, 0.3);
            }

            .btn:disabled {
                background: #ccc;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }

            /* Response Panel */
            .response-panel {
                background: var(--card-bg);
                padding: 25px;
                border-radius: 15px;
                box-shadow: var(--shadow);
                border: 1px solid var(--border-color);
                margin-bottom: 20px;
            }

            .loading {
                display: none;
                text-align: center;
                padding: 20px;
                color: var(--primary-color);
            }

            .spinner {
                width: 40px;
                height: 40px;
                border: 4px solid var(--border-color);
                border-left: 4px solid var(--primary-color);
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 15px;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .answer {
                line-height: 1.8;
                font-size: 1.1rem;
                color: var(--text-color);
            }

            .citations {
                margin-top: 20px;
                padding-top: 20px;
                border-top: 2px solid var(--border-color);
            }

            .citation {
                background: #f8f9fa;
                padding: 15px;
                margin-bottom: 10px;
                border-radius: 8px;
                border-left: 4px solid var(--primary-color);
            }

            .citation-title {
                font-weight: 600;
                color: var(--primary-color);
                margin-bottom: 5px;
            }

            .citation-url {
                color: #666;
                font-size: 0.9rem;
                text-decoration: none;
            }

            .citation-url:hover {
                text-decoration: underline;
            }

            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin-top: 20px;
                padding-top: 20px;
                border-top: 2px solid var(--border-color);
            }

            .stat-item {
                text-align: center;
                background: var(--bg-color);
                padding: 15px;
                border-radius: 10px;
            }

            .stat-value {
                font-size: 1.5rem;
                font-weight: bold;
                color: var(--primary-color);
            }

            .stat-label {
                font-size: 0.9rem;
                color: var(--text-color);
                opacity: 0.8;
            }

            /* Error styles */
            .error {
                background: #ffebee;
                color: #c62828;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #f44336;
                margin-top: 15px;
            }

            /* Responsive design */
            @media (max-width: 768px) {
                .main-content {
                    grid-template-columns: 1fr;
                }
                
                .header h1 {
                    font-size: 2rem;
                }
                
                .container {
                    padding: 10px;
                }
                
                .voice-button {
                    width: 100px;
                    height: 100px;
                    font-size: 1.5rem;
                }
            }

            /* Hide file input */
            .file-input {
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Header -->
            <div class="header">
                <h1>🌾 Agriculture Bot Searcher</h1>
                <p>Advanced Agricultural Assistant with Voice & Text Input</p>
            </div>

            <!-- Main Content -->
            <div class="main-content">
                <!-- Configuration Panel -->
                <div class="config-panel">
                    <h3>⚙️ Configuration</h3>
                    
                    <div class="form-group">
                        <label for="base-port">Ollama Base Port:</label>
                        <input type="number" id="base-port" class="form-control" value="11434" min="1024" max="65535">
                    </div>
                    
                    <div class="form-group">
                        <label for="num-agents">Number of Agents:</label>
                        <div class="form-control-inline">
                            <input type="range" id="num-agents" min="1" max="6" value="2" class="form-control">
                            <span class="value-display" id="agents-value">2</span>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="num-searches">Web Searches per Query:</label>
                        <div class="form-control-inline">
                            <input type="range" id="num-searches" min="1" max="5" value="2" class="form-control">
                            <span class="value-display" id="searches-value">2</span>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>Answer Mode:</label>
                        <div class="radio-group">
                            <label class="radio-option">
                                <input type="radio" id="detailed-mode" name="answer-mode" value="detailed" checked>
                                📝 Detailed
                            </label>
                            <label class="radio-option">
                                <input type="radio" id="exact-mode" name="answer-mode" value="exact">
                                🎯 Exact
                            </label>
                        </div>
                    </div>
                </div>

                <!-- Voice Input Panel -->
                <div class="voice-panel">
                    <h3>🎤 Voice Input</h3>
                    
                    <div class="form-group">
                        <label for="language-select">Language:</label>
                        <select id="language-select" class="form-control language-selector">
                            <option value="mr">🇮🇳 Marathi (मराठी)</option>
                            <option value="hi">🇮🇳 Hindi (हिंदी)</option>
                            <option value="bn">🇮🇳 Bengali (বাংলা)</option>
                            <option value="te">🇮🇳 Telugu (తెలుగు)</option>
                            <option value="ta">🇮🇳 Tamil (தமிழ்)</option>
                            <option value="gu">🇮🇳 Gujarati (ગુજરાતી)</option>
                            <option value="kn">🇮🇳 Kannada (ಕನ್ನಡ)</option>
                            <option value="ml">🇮🇳 Malayalam (മലയാളം)</option>
                            <option value="pa">🇮🇳 Punjabi (ਪੰਜਾਬੀ)</option>
                            <option value="or">🇮🇳 Odia (ଓଡ଼ିଆ)</option>
                        </select>
                    </div>
                    
                    <div class="voice-controls">
                        <button id="voice-button" class="voice-button" onclick="toggleVoiceRecording()">
                            🎤
                        </button>
                        <div id="voice-status" class="voice-status idle">
                            Click to start voice input
                        </div>
                        
                        <!-- Hidden file input for audio upload -->
                        <input type="file" id="audio-file" class="file-input" accept="audio/*" onchange="processAudioFile()">
                        <button onclick="document.getElementById('audio-file').click()" class="btn" style="width: auto; margin-top: 10px;">
                            📁 Upload Audio File
                        </button>
                    </div>
                </div>
            </div>

            <!-- Query Panel -->
            <div class="query-panel">
                <h3>💬 Your Query</h3>
                <div class="form-group">
                    <label for="query-input">Enter your agricultural query (or use voice input above):</label>
                    <textarea 
                        id="query-input" 
                        class="form-control query-input" 
                        placeholder="Ask about crops, diseases, farming techniques, weather, markets, or any agricultural topic..."
                        rows="4"
                    ></textarea>
                </div>
                <button onclick="submitQuery()" class="btn" id="submit-btn">
                    🔍 Search & Analyze
                </button>
            </div>

            <!-- Response Panel -->
            <div class="response-panel" id="response-panel" style="display: none;">
                <h3>🤖 Assistant Response</h3>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Processing your query... This may take a moment.</p>
                </div>
                
                <div id="response-content" style="display: none;">
                    <div class="answer" id="answer"></div>
                    
                    <div class="citations" id="citations-section" style="display: none;">
                        <h4>📚 Sources & Citations</h4>
                        <div id="citations"></div>
                    </div>
                    
                    <div class="stats" id="stats-section" style="display: none;">
                        <div class="stat-item">
                            <div class="stat-value" id="execution-time">-</div>
                            <div class="stat-label">Execution Time (s)</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" id="agents-used">-</div>
                            <div class="stat-label">Agents Used</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" id="citations-count">-</div>
                            <div class="stat-label">Citations</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" id="search-results">-</div>
                            <div class="stat-label">Search Results</div>
                        </div>
                    </div>
                </div>
                
                <div id="error-content" style="display: none;">
                    <div class="error" id="error-message"></div>
                </div>
            </div>
        </div>

        <script>
            // Global variables
            let mediaRecorder;
            let audioChunks = [];
            let isRecording = false;
            
            // Initialize page
            document.addEventListener('DOMContentLoaded', function() {
                checkSystemStatus();
                setupEventListeners();
            });
            
            function setupEventListeners() {
                // Range input updates
                document.getElementById('num-agents').addEventListener('input', function(e) {
                    document.getElementById('agents-value').textContent = e.target.value;
                });
                
                document.getElementById('num-searches').addEventListener('input', function(e) {
                    document.getElementById('searches-value').textContent = e.target.value;
                });
                
                // Enter key to submit
                document.getElementById('query-input').addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' && !e.ctrlKey && !e.shiftKey) {
                        e.preventDefault();
                        submitQuery();
                    }
                });
            }
            
            async function checkSystemStatus() {
                try {
                    const basePort = document.getElementById('base-port').value;
                    const response = await fetch(`/api/status?base_port=${basePort}`);
                    const data = await response.json();
                    
                    if (!data.success) {
                        console.warn('System status check failed:', data.error);
                    }
                } catch (error) {
                    console.error('Status check error:', error);
                }
            }
            
            async function toggleVoiceRecording() {
                if (isRecording) {
                    stopRecording();
                } else {
                    startRecording();
                }
            }
            
            async function startRecording() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = function(event) {
                        audioChunks.push(event.data);
                    };
                    
                    mediaRecorder.onstop = function() {
                        processRecordedAudio();
                    };
                    
                    mediaRecorder.start();
                    isRecording = true;
                    
                    // Update UI
                    const button = document.getElementById('voice-button');
                    const status = document.getElementById('voice-status');
                    
                    button.classList.add('recording');
                    button.innerHTML = '⏹️';
                    status.textContent = 'Recording... Click to stop';
                    status.className = 'voice-status recording';
                    
                } catch (error) {
                    console.error('Error starting recording:', error);
                    alert('Error accessing microphone. Please check permissions.');
                }
            }
            
            function stopRecording() {
                if (mediaRecorder && isRecording) {
                    mediaRecorder.stop();
                    mediaRecorder.stream.getTracks().forEach(track => track.stop());
                    isRecording = false;
                    
                    // Update UI
                    const button = document.getElementById('voice-button');
                    const status = document.getElementById('voice-status');
                    
                    button.classList.remove('recording');
                    button.classList.add('processing');
                    button.innerHTML = '⏳';
                    status.textContent = 'Processing audio...';
                    status.className = 'voice-status processing';
                }
            }
            
            async function processRecordedAudio() {
                try {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    await transcribeAudio(audioBlob);
                } catch (error) {
                    console.error('Error processing recorded audio:', error);
                    resetVoiceUI('Error processing audio');
                }
            }
            
            async function processAudioFile() {
                const fileInput = document.getElementById('audio-file');
                const file = fileInput.files[0];
                
                if (!file) return;
                
                // Update UI
                const status = document.getElementById('voice-status');
                status.textContent = 'Processing uploaded file...';
                status.className = 'voice-status processing';
                
                try {
                    await transcribeAudio(file);
                } catch (error) {
                    console.error('Error processing audio file:', error);
                    resetVoiceUI('Error processing audio file');
                }
            }
            
            async function transcribeAudio(audioBlob) {
                try {
                    const formData = new FormData();
                    formData.append('audio', audioBlob);
                    formData.append('language', document.getElementById('language-select').value);
                    
                    const response = await fetch('/api/transcribe', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        // Use translation if available, otherwise use transcription
                        const text = data.translation || data.transcription;
                        document.getElementById('query-input').value = text;
                        resetVoiceUI('Transcription successful!');
                        
                        // Auto-submit if text is not empty
                        if (text.trim()) {
                            setTimeout(() => submitQuery(), 1000);
                        }
                    } else {
                        resetVoiceUI(`Transcription failed: ${data.error}`);
                    }
                } catch (error) {
                    console.error('Transcription error:', error);
                    resetVoiceUI('Network error during transcription');
                }
            }
            
            function resetVoiceUI(message = 'Click to start voice input') {
                const button = document.getElementById('voice-button');
                const status = document.getElementById('voice-status');
                
                button.classList.remove('recording', 'processing');
                button.innerHTML = '🎤';
                status.textContent = message;
                status.className = 'voice-status idle';
                
                // Reset to default message after a delay
                if (message !== 'Click to start voice input') {
                    setTimeout(() => {
                        status.textContent = 'Click to start voice input';
                    }, 3000);
                }
            }
            
            async function submitQuery() {
                const query = document.getElementById('query-input').value.trim();
                if (!query) {
                    alert('Please enter a query or use voice input.');
                    return;
                }
                
                // Show loading
                document.getElementById('response-panel').style.display = 'block';
                document.getElementById('loading').style.display = 'block';
                document.getElementById('response-content').style.display = 'none';
                document.getElementById('error-content').style.display = 'none';
                document.getElementById('submit-btn').disabled = true;
                
                try {
                    const requestData = {
                        query: query,
                        base_port: parseInt(document.getElementById('base-port').value),
                        num_agents: parseInt(document.getElementById('num-agents').value),
                        num_searches: parseInt(document.getElementById('num-searches').value),
                        exact_answer: document.getElementById('exact-mode').checked
                    };
                    
                    const response = await fetch('/api/query', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(requestData)
                    });
                    
                    const data = await response.json();
                    
                    // Hide loading
                    document.getElementById('loading').style.display = 'none';
                    
                    if (data.success) {
                        displayAnswer(data);
                    } else {
                        displayError(data.error || 'Unknown error occurred');
                    }
                    
                } catch (error) {
                    console.error('Query error:', error);
                    document.getElementById('loading').style.display = 'none';
                    displayError('Network error. Please check your connection.');
                } finally {
                    document.getElementById('submit-btn').disabled = false;
                }
            }
            
            function displayAnswer(data) {
                document.getElementById('answer').innerHTML = formatAnswer(data.answer);
                document.getElementById('response-content').style.display = 'block';
                
                // Display citations
                if (data.citations && data.citations.length > 0) {
                    displayCitations(data.citations);
                    document.getElementById('citations-section').style.display = 'block';
                } else {
                    document.getElementById('citations-section').style.display = 'none';
                }
                
                // Display stats
                if (data.stats) {
                    displayStats(data.stats);
                    document.getElementById('stats-section').style.display = 'block';
                } else {
                    document.getElementById('stats-section').style.display = 'none';
                }
            }
            
            function formatAnswer(answer) {
                // Convert newlines to HTML line breaks
                return answer.replace(/\\n/g, '<br>').replace(/\\n\\n/g, '<br><br>');
            }
            
            function displayCitations(citations) {
                const citationsContainer = document.getElementById('citations');
                citationsContainer.innerHTML = '';
                
                citations.forEach((citation, index) => {
                    const citationElement = document.createElement('div');
                    citationElement.className = 'citation';
                    citationElement.innerHTML = `
                        <div class="citation-title">[${index + 1}] ${citation.title}</div>
                        <a href="${citation.url}" target="_blank" class="citation-url">${citation.url}</a>
                        ${citation.snippet ? `<div style="margin-top: 5px; font-style: italic;">${citation.snippet}</div>` : ''}
                    `;
                    citationsContainer.appendChild(citationElement);
                });
            }
            
            function displayStats(stats) {
                document.getElementById('execution-time').textContent = stats.execution_time || '-';
                document.getElementById('agents-used').textContent = stats.agents_used || '-';
                document.getElementById('citations-count').textContent = stats.citations_count || '-';
                document.getElementById('search-results').textContent = stats.search_results || '-';
            }
            
            function displayError(error) {
                document.getElementById('error-message').textContent = error;
                document.getElementById('error-content').style.display = 'block';
            }
        </script>
    </body>
    </html>
    """

    @app.route('/')
    def index():
        """Serve the main web interface"""
        return render_template_string(HTML_TEMPLATE)

    @app.route('/api/status')
    def status():
        """Get system status and available Ollama instances"""
        try:
            base_port = int(request.args.get('base_port', 11434))
            bot = get_chatbot_instance(base_port, 2)
            transcriber = get_transcriber_instance()
            
            # Check transcriber status
            transcriber_status = transcriber.is_model_ready()
            
            return jsonify({
                "success": True,
                "chatbot_ready": True,
                "voice_transcription": transcriber_status,
                "supported_languages": transcriber.get_supported_languages(),
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    @app.route('/api/transcribe', methods=['POST'])
    def transcribe():
        """Process voice transcription"""
        try:
            if 'audio' not in request.files:
                return jsonify({"success": False, "error": "No audio file provided"}), 400
            
            audio_file = request.files['audio']
            language = request.form.get('language', 'mr')
            
            # Save audio file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                audio_file.save(temp_file.name)
                temp_path = temp_file.name
            
            try:
                # Get transcriber and process
                transcriber = get_transcriber_instance()
                result = transcriber.transcribe_audio(
                    audio_path=temp_path,
                    language=language,
                    translate_to_english=True
                )
                
                return jsonify(result)
                
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
        except Exception as e:
            logging.error(f"Transcription error: {str(e)}")
            return jsonify({
                "success": False,
                "error": f"Transcription failed: {str(e)}"
            }), 500

    @app.route('/api/query', methods=['POST'])
    def query():
        """Process agriculture query"""
        try:
            data = request.get_json()
            
            query_text = data.get('query', '').strip()
            if not query_text:
                return jsonify({"success": False, "error": "Query is required"}), 400
            
            base_port = int(data.get('base_port', 11434))
            num_agents = int(data.get('num_agents', 2))
            num_searches = int(data.get('num_searches', 2))
            exact_answer = bool(data.get('exact_answer', False))
            
            # Get chatbot instance with specified parameters
            bot = get_chatbot_instance(base_port, num_agents)
            
            # Process query
            start_time = time.time()
            result = bot.answer_query(
                query=query_text,
                num_searches=num_searches,
                exact_answer=exact_answer
            )
            execution_time = round(time.time() - start_time, 1)
            
            if result["success"]:
                # Prepare response with stats
                response = {
                    "success": True,
                    "answer": result["answer"],
                    "citations": result.get("citations", []),
                    "stats": {
                        "execution_time": execution_time,
                        "agents_used": result.get("agents_used", 1),
                        "citations_count": len(result.get("citations", [])),
                        "search_results": result.get("search_results_count", 0)
                    }
                }
                return jsonify(response)
            else:
                return jsonify({
                    "success": False,
                    "error": result.get("error", "Unknown error occurred"),
                    "answer": result.get("answer", "Sorry, I couldn't process your query.")
                })
                
        except Exception as e:
            logging.error(f"Query processing error: {str(e)}")
            return jsonify({
                "success": False,
                "error": f"Server error: {str(e)}"
            }), 500

    def run_server(host='0.0.0.0', port=5000, debug=False):
        """Run the Flask development server"""
        if not HAS_FLASK:
            print("Flask is not installed. Please install it with: pip install flask flask-cors")
            return
        
        print(f"🌾 Agriculture Bot Searcher - Voice & Text Interface")
        print(f"🚀 Starting server on http://{host}:{port}")
        print(f"📝 Make sure Ollama is running on the configured ports")
        print(f"🎤 Voice transcription ready for Indian languages")
        print(f"🔧 Default configuration: Base port 11434, 2 agents")
        
        app.run(host=host, port=port, debug=debug)

else:
    def run_server(*args, **kwargs):
        print("Flask is not installed. Please install it with: pip install flask flask-cors")

if __name__ == '__main__':
    run_server(debug=True)
