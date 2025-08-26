// Enhanced IndicAgri Bot JavaScript with RAG Pipeline Support

// Global variables
let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let isProcessing = false;
let currentResponseData = null;
let stream = null;

// DOM elements cache
let domElements = {};

// Initialize DOM elements after page load
function initializeDOMElements() {
    domElements = {
        // Enhanced RAG Controls
        enableDatabaseSearch: document.getElementById('enable-database-search'),
        enableWebSearch: document.getElementById('enable-web-search'),
        numSubQueriesSlider: document.getElementById('num-sub-queries'),
        numSubQueriesValue: document.getElementById('num-sub-queries-value'),
        dbChunksSlider: document.getElementById('db-chunks-per-query'),
        dbChunksValue: document.getElementById('db-chunks-per-query-value'),
        webResultsSlider: document.getElementById('web-results-per-query'),
        webResultsValue: document.getElementById('web-results-per-query-value'),
        synthesisModelSelect: document.getElementById('synthesis-model'),
        refreshModelsBtn: document.getElementById('refresh-models'),

        // Voice Controls
        recordBtn: document.getElementById('record-btn'),
        recordingStatus: document.getElementById('recording-status'),
        languageSelect: document.getElementById('language-select'),
        apiKeyInput: document.getElementById('api-key'),
        hfTokenInput: document.getElementById('hf-token'),
        useLocalModelCheck: document.getElementById('use-local-model'),

        // Text Input
        userInput: document.getElementById('user-input'),
        sendBtn: document.getElementById('send-btn'),

        // Response Panel
        responseTabs: document.querySelectorAll('.tab-btn'),
        tabPanes: document.querySelectorAll('.tab-pane'),
        responseContent: document.getElementById('response-content'),
        pipelineInfo: document.getElementById('pipeline-info'),
        markdownContent: document.getElementById('markdown-content'),
        citationsContent: document.getElementById('citations-content'),
        downloadMarkdownBtn: document.getElementById('download-markdown'),
        loadingIndicator: document.getElementById('loading-indicator'),

        // Status Panel
        ragStatus: document.getElementById('rag-status'),
        voiceStatus: document.getElementById('voice-status'),
        modelsStatus: document.getElementById('models-status'),
        refreshStatusBtn: document.getElementById('refresh-status')
    };
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌾 Initializing Enhanced IndicAgri Bot...');
    
    // Check browser compatibility first
    checkBrowserCompatibility();
    
    initializeDOMElements();
    initializeApp();
    initializeEventListeners();
    checkSystemStatus();
    loadAvailableModels();
});

// Check browser compatibility and show helpful messages
function checkBrowserCompatibility() {
    const userAgent = navigator.userAgent.toLowerCase();
    const isChrome = userAgent.includes('chrome') && !userAgent.includes('edg');
    const isFirefox = userAgent.includes('firefox');
    const isSafari = userAgent.includes('safari') && !userAgent.includes('chrome');
    const isEdge = userAgent.includes('edg');
    
    console.log('🌐 Browser detection:', { isChrome, isFirefox, isSafari, isEdge });
    
    if (!isChrome && !isFirefox && !isSafari && !isEdge) {
        showNotification('⚠️ For best experience, please use Chrome, Firefox, Safari, or Edge browser.', 'warning');
    }
    
    // Check HTTPS
    const isSecureContext = window.isSecureContext || 
                           location.protocol === 'https:' || 
                           location.hostname === 'localhost' || 
                           location.hostname === '127.0.0.1' ||
                           location.hostname.endsWith('.local');
    
    console.log('🔒 Secure context:', isSecureContext, 'Protocol:', location.protocol);
    
    if (!isSecureContext) {
        showNotification('🔒 Microphone requires HTTPS or localhost. Some features may be limited on HTTP.', 'warning');
    }
    
    // Check for critical APIs
    const hasModernMedia = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
    const hasLegacyMedia = !!(navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia);
    const hasMediaRecorder = !!window.MediaRecorder;
    
    console.log('🎤 Media APIs:', { hasModernMedia, hasLegacyMedia, hasMediaRecorder });
    
    if (!hasModernMedia && !hasLegacyMedia) {
        showNotification('❌ Microphone not supported in this browser. Voice features will be disabled.', 'error');
    }
    
    if (!hasMediaRecorder) {
        showNotification('❌ Audio recording not supported. Please update your browser for voice features.', 'error');
    }
    
    // Show initial guidance
    if (hasModernMedia || hasLegacyMedia) {
        setTimeout(() => {
            showNotification('💡 To use voice features: Click the microphone button and allow access when your browser prompts you.', 'info');
        }, 2000);
    }
}

// Main initialization function
function initializeApp() {
    console.log('Setting up Enhanced IndicAgri Bot interface...');
    
    // Initialize sliders
    updateSliderValues();
    
    // Check microphone permissions and availability
    checkMicrophonePermissions();
    
    console.log('✅ IndicAgri Bot initialized successfully');
}

// Check microphone permissions and availability
async function checkMicrophonePermissions() {
    try {
        console.log('🎤 Checking microphone permissions...');
        
        // First check if we're on a secure context
        const isSecureContext = window.isSecureContext || 
                               location.protocol === 'https:' || 
                               location.hostname === 'localhost' || 
                               location.hostname === '127.0.0.1' ||
                               location.hostname.endsWith('.local');
        
        if (!isSecureContext) {
            console.warn('⚠️ Not in secure context - microphone requires HTTPS');
            updateVoiceStatus('⚠️ Requires HTTPS');
            showNotification('🔒 Microphone access requires HTTPS. Please access the site via HTTPS or localhost.', 'warning');
            return;
        }

        // Check for different getUserMedia implementations
        let getUserMedia = null;
        
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            // Modern API (preferred)
            getUserMedia = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
            console.log('✅ Using modern mediaDevices API');
        } else if (navigator.getUserMedia) {
            // Legacy API
            getUserMedia = navigator.getUserMedia.bind(navigator);
            console.log('⚠️ Using legacy getUserMedia API');
        } else if (navigator.webkitGetUserMedia) {
            // Webkit legacy
            getUserMedia = navigator.webkitGetUserMedia.bind(navigator);
            console.log('⚠️ Using webkit getUserMedia API');
        } else if (navigator.mozGetUserMedia) {
            // Mozilla legacy
            getUserMedia = navigator.mozGetUserMedia.bind(navigator);
            console.log('⚠️ Using mozilla getUserMedia API');
        }
        
        if (!getUserMedia) {
            console.warn('❌ No getUserMedia API available');
            updateVoiceStatus('❌ Not supported');
            showNotification('❌ Microphone not supported in this browser. Please use Chrome, Firefox, or Safari with HTTPS.', 'error');
            return;
        }

        // Test microphone access with user-friendly prompt
        console.log('🎤 Requesting microphone permission...');
        showNotification('🎤 Please allow microphone access when prompted by your browser.', 'info');
        
        // For modern API
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 44100
                }
            });
            
            console.log('✅ Microphone permission granted via modern API');
            updateVoiceStatus('✓ Microphone ready');
            showNotification('✅ Microphone access granted! You can now use voice input.', 'success');
            
            // Stop the test stream
            stream.getTracks().forEach(track => track.stop());
        } else {
            // For legacy APIs, wrap in Promise
            const stream = await new Promise((resolve, reject) => {
                getUserMedia({ audio: true }, resolve, reject);
            });
            
            console.log('✅ Microphone permission granted via legacy API');
            updateVoiceStatus('✓ Microphone ready (legacy)');
            showNotification('✅ Microphone access granted! You can now use voice input.', 'success');
            
            // Stop the test stream
            if (stream.getTracks) {
                stream.getTracks().forEach(track => track.stop());
            } else if (stream.stop) {
                stream.stop();
            }
        }
        
    } catch (error) {
        console.error('❌ Microphone permission error:', error);
        
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
            updateVoiceStatus('❌ Permission denied');
            showNotification('🚫 Microphone access denied. Please click the microphone icon in your browser\'s address bar and allow access, then refresh the page.', 'error');
        } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
            updateVoiceStatus('❌ No microphone found');
            showNotification('🎤 No microphone detected. Please connect a microphone and try again.', 'error');
        } else if (error.name === 'NotSupportedError' || error.name === 'NotSupportedError') {
            updateVoiceStatus('❌ Not supported');
            showNotification('❌ Microphone not supported in this browser. Please use Chrome, Firefox, or Safari.', 'error');
        } else if (error.name === 'SecurityError') {
            updateVoiceStatus('❌ Security error');
            showNotification('🔒 Security error: Please ensure you\'re accessing the site via HTTPS or localhost.', 'error');
        } else {
            updateVoiceStatus('❌ Error: ' + error.name);
            showNotification('❌ Microphone error: ' + error.message + '. Please check your browser settings and try again.', 'error');
        }
        
        // Show additional help
        setTimeout(() => {
            showNotification('💡 Tip: Look for a microphone icon in your browser\'s address bar and click "Allow" when prompted.', 'info');
        }, 3000);
    }
}

// Initialize event listeners
function initializeEventListeners() {
    console.log('Setting up event listeners...');
    
    // Voice recording
    if (domElements.recordBtn) {
        domElements.recordBtn.addEventListener('click', toggleRecording);
    }

    // Text input
    if (domElements.sendBtn) {
        domElements.sendBtn.addEventListener('click', sendTextQuery);
    }
    
    if (domElements.userInput) {
        domElements.userInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendTextQuery();
            }
        });
    }

    // Sliders
    if (domElements.numSubQueriesSlider) {
        domElements.numSubQueriesSlider.addEventListener('input', updateSliderValues);
    }
    if (domElements.dbChunksSlider) {
        domElements.dbChunksSlider.addEventListener('input', updateSliderValues);
    }
    if (domElements.webResultsSlider) {
        domElements.webResultsSlider.addEventListener('input', updateSliderValues);
    }

    // Buttons
    if (domElements.refreshModelsBtn) {
        domElements.refreshModelsBtn.addEventListener('click', loadAvailableModels);
    }
    if (domElements.downloadMarkdownBtn) {
        domElements.downloadMarkdownBtn.addEventListener('click', downloadMarkdown);
    }
    if (domElements.refreshStatusBtn) {
        domElements.refreshStatusBtn.addEventListener('click', checkSystemStatus);
    }

    // Tab navigation
    domElements.responseTabs.forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });
    
    console.log('✅ Event listeners initialized');
}

// Toggle recording function
async function toggleRecording() {
    if (isRecording) {
        stopRecording();
    } else {
        await startRecording();
    }
}

// Start recording function
async function startRecording() {
    try {
        console.log('🎤 Starting voice recording...');
        
        // Check for microphone support with multiple fallbacks
        let getUserMedia = null;
        
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            // Modern API (preferred)
            getUserMedia = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
        } else if (navigator.getUserMedia) {
            // Legacy API
            getUserMedia = navigator.getUserMedia.bind(navigator);
        } else if (navigator.webkitGetUserMedia) {
            // Webkit legacy
            getUserMedia = navigator.webkitGetUserMedia.bind(navigator);
        } else if (navigator.mozGetUserMedia) {
            // Mozilla legacy
            getUserMedia = navigator.mozGetUserMedia.bind(navigator);
        }
        
        if (!getUserMedia) {
            throw new Error('Microphone not supported in this browser. Please use Chrome, Firefox, or Safari with HTTPS.');
        }
        
        // Check secure context
        const isSecureContext = window.isSecureContext || 
                               location.protocol === 'https:' || 
                               location.hostname === 'localhost' || 
                               location.hostname === '127.0.0.1' ||
                               location.hostname.endsWith('.local');
        
        if (!isSecureContext) {
            throw new Error('Microphone requires HTTPS or localhost for security. Please access via HTTPS.');
        }
        
        // Get audio stream with robust API handling
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            // Modern API
            stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 44100
                }
            });
        } else {
            // Legacy API - wrap in Promise
            stream = await new Promise((resolve, reject) => {
                getUserMedia({ audio: true }, resolve, reject);
            });
        }
        
        // Check if MediaRecorder is supported
        if (!window.MediaRecorder) {
            throw new Error('MediaRecorder not supported in this browser. Please update your browser.');
        }
        
        // Check for codec support
        let mimeType = 'audio/webm';
        if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
            mimeType = 'audio/webm;codecs=opus';
        } else if (MediaRecorder.isTypeSupported('audio/wav')) {
            mimeType = 'audio/wav';
        } else {
            console.warn('⚠️ Preferred audio codecs not supported, using default');
        }
        
        // Create MediaRecorder
        mediaRecorder = new MediaRecorder(stream, { mimeType: mimeType });
        audioChunks = [];
        
        mediaRecorder.ondataavailable = function(event) {
            console.log('📊 Audio data available:', event.data.size, 'bytes');
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };
        
        mediaRecorder.onstop = function() {
            console.log('⏹️ Recording stopped');
            processRecording();
        };
        
        mediaRecorder.onerror = function(event) {
            console.error('❌ MediaRecorder error:', event.error);
            showNotification('Recording error: ' + (event.error.name || event.error), 'error');
            stopRecording();
        };
        
        // Start recording
        mediaRecorder.start(1000); // Record in 1-second chunks
        isRecording = true;
        
        updateRecordingUI(true);
        showNotification('🎤 Recording started! Speak clearly into your microphone...', 'info');
        console.log('✅ Recording started successfully');
        
    } catch (error) {
        console.error('❌ Error starting recording:', error);
        stopRecording();
        
        // Provide specific error guidance
        let errorMessage = error.message;
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
            errorMessage = 'Microphone access denied. Please allow microphone access and try again.';
            showNotification('🚫 ' + errorMessage + ' Look for the microphone icon in your browser\'s address bar and click "Allow".', 'error');
        } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
            errorMessage = 'No microphone found. Please connect a microphone and try again.';
            showNotification('🎤 ' + errorMessage, 'error');
        } else if (error.name === 'NotSupportedError') {
            errorMessage = 'Microphone not supported. Please use Chrome, Firefox, or Safari.';
            showNotification('❌ ' + errorMessage, 'error');
        } else if (error.name === 'SecurityError') {
            errorMessage = 'Security error. Please ensure you\'re using HTTPS or localhost.';
            showNotification('🔒 ' + errorMessage, 'error');
        } else {
            showNotification('❌ Recording failed: ' + errorMessage, 'error');
        }
        
        logMessage(`[ERROR] Failed to start recording: ${errorMessage}`, 'error');
        updateVoiceStatus('❌ Recording failed');
    }
}

// Stop recording function
function stopRecording() {
    console.log('⏹️ Stopping recording...');
    
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        updateRecordingUI(false);
        
        // Stop all tracks
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
        
        console.log('✅ Recording stopped');
        showNotification('Recording stopped. Processing audio...', 'info');
    }
}

// Process recording
async function processRecording() {
    if (audioChunks.length === 0) {
        console.warn('⚠️ No audio data recorded');
        showNotification('No audio recorded. Please try again.', 'warning');
        return;
    }
    
    console.log('🔄 Processing audio recording...');
    isProcessing = true;
    updateProcessingUI(true);
    
    try {
        // Create audio blob
        const audioBlob = new Blob(audioChunks, { 
            type: mediaRecorder.mimeType || 'audio/webm'
        });
        
        console.log('📦 Created audio blob:', audioBlob.size, 'bytes, type:', audioBlob.type);
        
        // Create form data
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');
        formData.append('language', domElements.languageSelect?.value || 'en');
        formData.append('use_local_model', domElements.useLocalModelCheck?.checked || true);
        
        if (domElements.apiKeyInput?.value) {
            formData.append('api_key', domElements.apiKeyInput.value);
        }
        if (domElements.hfTokenInput?.value) {
            formData.append('hf_token', domElements.hfTokenInput.value);
        }
        
        console.log('📤 Sending audio to server for transcription...');
        
        // Send to server
        const response = await fetch('/transcribe', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        console.log('📥 Transcription response:', result);
        
        if (result.success) {
            // Handle different response formats
            const transcribedText = result.english_text || result.original_text || result.text || '';
            console.log('✅ Transcription successful:', transcribedText);
            
            // Check if it's an error message
            if (transcribedText.includes('API key required') || transcribedText.includes('error')) {
                showNotification('🔑 ' + transcribedText, 'warning');
                updateVoiceStatus('⚠️ API key needed');
                return;
            }
            
            if (domElements.userInput && transcribedText.trim()) {
                domElements.userInput.value = transcribedText;
                showNotification('Voice transcribed: "' + transcribedText.substring(0, 50) + '..."', 'success');
                
                // Auto-send if text is transcribed and not empty
                setTimeout(() => sendTextQuery(), 1000);
            } else {
                showNotification('❌ No text transcribed. Please try again.', 'warning');
            }
        } else {
            throw new Error(result.error || 'Transcription failed');
        }
        
    } catch (error) {
        console.error('❌ Error processing recording:', error);
        showNotification('Transcription failed: ' + error.message, 'error');
    } finally {
        isProcessing = false;
        updateProcessingUI(false);
        audioChunks = []; // Clear audio chunks
    }
}

// Send text query
async function sendTextQuery() {
    const query = domElements.userInput?.value?.trim();
    if (!query) {
        showNotification('Please enter a question or record voice input', 'warning');
        return;
    }
    
    console.log('📤 Sending query:', query);
    showLoading(true);
    
    try {
        const requestData = {
            query: query,
            enable_database_search: domElements.enableDatabaseSearch?.checked ?? true,
            enable_web_search: domElements.enableWebSearch?.checked ?? true,
            num_sub_queries: parseInt(domElements.numSubQueriesSlider?.value || 3),
            db_chunks_per_query: parseInt(domElements.dbChunksSlider?.value || 3),
            web_results_per_query: parseInt(domElements.webResultsSlider?.value || 3),
            synthesis_model: domElements.synthesisModelSelect?.value || 'llama3.2:3b'
        };
        
        console.log('📋 Request data:', requestData);
        
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const result = await response.json();
        console.log('📥 Search response:', result);
        
        if (result.success) {
            currentResponseData = result;
            displayResults(result);
            showNotification('Search completed successfully!', 'success');
        } else {
            throw new Error(result.error || 'Search failed');
        }
        
    } catch (error) {
        console.error('❌ Error sending query:', error);
        showNotification('Search failed: ' + error.message, 'error');
        displayError(error.message);
    } finally {
        showLoading(false);
    }
}

// Display results in the UI
function displayResults(data) {
    console.log('📊 Displaying results:', data);
    
    // Clear previous results
    clearResults();
    
    // Display pipeline information
    displayPipelineInfo(data);
    
    // Display main response
    displayMainResponse(data.response || data.answer);
    
    // Display markdown content
    displayMarkdownContent(data.markdown_report);
    
    // Display citations
    displayCitations(data.citations);
    
    // Switch to response tab
    switchTab('response');
}

// Display pipeline information
function displayPipelineInfo(data) {
    if (!domElements.pipelineInfo) return;
    
    let pipelineHtml = '<div class="pipeline-steps">';
    
    // Query refinement
    if (data.refined_query || data.original_query) {
        pipelineHtml += `
            <div class="pipeline-step">
                <h4>🔍 Query Refinement</h4>
                <p><strong>Original:</strong> ${data.original_query || data.query}</p>
                ${data.refined_query ? `<p><strong>Refined:</strong> ${data.refined_query}</p>` : ''}
            </div>
        `;
    }
    
    // Sub-queries
    if (data.sub_queries && data.sub_queries.length > 0) {
        pipelineHtml += `
            <div class="pipeline-step">
                <h4>🔀 Sub-queries Generated</h4>
                <ul>
                    ${data.sub_queries.map(sq => `<li>${sq}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    // Database search results
    if (data.database_results && data.database_results.length > 0) {
        pipelineHtml += `
            <div class="pipeline-step">
                <h4>🗄️ Database Search Results</h4>
                <p>Found ${data.database_results.length} relevant chunks</p>
                <div class="search-results">
                    ${data.database_results.slice(0, 3).map(result => `
                        <div class="search-result">
                            <strong>Score:</strong> ${result.score?.toFixed(3) || 'N/A'}<br>
                            <strong>Source:</strong> ${result.source || 'Unknown'}<br>
                            <strong>Content:</strong> ${(result.content || result.text || '').substring(0, 200)}...
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Web search results
    if (data.web_results && data.web_results.length > 0) {
        pipelineHtml += `
            <div class="pipeline-step">
                <h4>🌐 Web Search Results</h4>
                <p>Found ${data.web_results.length} web sources</p>
                <div class="search-results">
                    ${data.web_results.slice(0, 3).map(result => `
                        <div class="search-result">
                            <strong>Title:</strong> ${result.title || 'Unknown'}<br>
                            <strong>URL:</strong> <a href="${result.href || result.url}" target="_blank">${result.href || result.url}</a><br>
                            <strong>Content:</strong> ${(result.body || result.content || '').substring(0, 200)}...
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    pipelineHtml += '</div>';
    domElements.pipelineInfo.innerHTML = pipelineHtml;
}

// Display main response
function displayMainResponse(response) {
    if (!domElements.responseContent) return;
    
    domElements.responseContent.innerHTML = `
        <div class="response-text">
            ${(response || 'No response available').replace(/\n/g, '<br>')}
        </div>
    `;
}

// Display markdown content
function displayMarkdownContent(markdown) {
    if (!domElements.markdownContent) return;
    
    domElements.markdownContent.innerHTML = `
        <pre class="markdown-content">${markdown || 'No markdown content available'}</pre>
    `;
}

// Display citations
function displayCitations(citations) {
    if (!domElements.citationsContent) return;
    
    if (!citations || citations.length === 0) {
        domElements.citationsContent.innerHTML = '<p class="placeholder-text">No citations available</p>';
        return;
    }
    
    const citationsHtml = citations.map((citation, index) => `
        <div class="citation">
            <h4>Citation ${index + 1}</h4>
            <p><strong>Source:</strong> ${citation.source || 'Unknown'}</p>
            <p><strong>Title:</strong> ${citation.title || 'N/A'}</p>
            ${citation.url ? `<p><strong>URL:</strong> <a href="${citation.url}" target="_blank">${citation.url}</a></p>` : ''}
            <p><strong>Content:</strong> ${citation.content || citation.text || 'No content'}</p>
        </div>
    `).join('');
    
    domElements.citationsContent.innerHTML = citationsHtml;
}

// Switch tabs
function switchTab(tabName) {
    // Update tab buttons
    domElements.responseTabs.forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
    });
    
    // Update tab panes
    domElements.tabPanes.forEach(pane => {
        pane.classList.toggle('active', pane.id === `${tabName}-pane`);
    });
}

// Update slider values
function updateSliderValues() {
    if (domElements.numSubQueriesSlider && domElements.numSubQueriesValue) {
        domElements.numSubQueriesValue.textContent = domElements.numSubQueriesSlider.value;
    }
    if (domElements.dbChunksSlider && domElements.dbChunksValue) {
        domElements.dbChunksValue.textContent = domElements.dbChunksSlider.value;
    }
    if (domElements.webResultsSlider && domElements.webResultsValue) {
        domElements.webResultsValue.textContent = domElements.webResultsSlider.value;
    }
}

// Load available models using ollama list
async function loadAvailableModels() {
    console.log('📋 Loading available models...');
    
    try {
        const response = await fetch('/models');
        const result = await response.json();
        
        if (result.success && domElements.synthesisModelSelect) {
            domElements.synthesisModelSelect.innerHTML = '';
            
            if (result.models && result.models.length > 0) {
                result.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model;
                    option.textContent = model;
                    domElements.synthesisModelSelect.appendChild(option);
                });
                console.log('✅ Loaded', result.models.length, 'models');
            } else {
                const option = document.createElement('option');
                option.value = 'llama3.2';
                option.textContent = 'llama3.2 (default)';
                domElements.synthesisModelSelect.appendChild(option);
                console.log('⚠️ No models found, using default');
            }
        }
    } catch (error) {
        console.error('❌ Error loading models:', error);
        showNotification('Failed to load models: ' + error.message, 'warning');
    }
}

// Check system status
async function checkSystemStatus() {
    console.log('🔍 Checking system status...');
    
    try {
        const response = await fetch('/health');
        const result = await response.json();
        
        console.log('📊 Health check result:', result);
        
        // Update Enhanced RAG status
        const ragStatus = result.components?.enhanced_rag ? '✓ Available' : '✗ Not available';
        updateRAGStatus(ragStatus);
        
        // Update Voice Transcription status
        let voiceStatus = '✗ Not available';
        if (result.components?.voice_transcription) {
            const methods = result.details?.voice_methods || [];
            voiceStatus = `✓ Available (${methods.join(', ')})`;
        } else if (result.components?.api_key_configured) {
            voiceStatus = '⚠ API key configured';
        }
        updateVoiceStatus(voiceStatus);
        
        // Update Models status
        let modelsStatus = '✗ No models';
        if (result.details?.ollama_models_count > 0) {
            modelsStatus = `✓ ${result.details.ollama_models_count} models`;
        } else if (result.components?.ollama_connection === false) {
            modelsStatus = '✗ Ollama not connected';
        }
        updateModelsStatus(modelsStatus);
        
        console.log('✅ System status updated');
        
        // Show warnings if needed
        if (!result.components?.api_key_configured && !result.components?.voice_transcription) {
            showNotification('💡 Voice features require SarvamAI API key. Configure it in settings for voice transcription.', 'info');
        }
        
        if (result.details?.rag_error) {
            console.warn('RAG system error:', result.details.rag_error);
        }
        
    } catch (error) {
        console.error('❌ Error checking status:', error);
        updateRAGStatus('✗ Connection error');
        updateVoiceStatus('✗ Connection error');
        updateModelsStatus('✗ Connection error');
        showNotification('Failed to check system status. Please check server connection.', 'error');
    }
}

// Download markdown
function downloadMarkdown() {
    if (!currentResponseData || !currentResponseData.markdown_report) {
        showNotification('No markdown content to download', 'warning');
        return;
    }
    
    const blob = new Blob([currentResponseData.markdown_report], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `indicagri_response_${new Date().toISOString().slice(0, 10)}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification('Markdown downloaded successfully!', 'success');
}

// UI update functions
function updateRecordingUI(recording) {
    if (domElements.recordBtn) {
        domElements.recordBtn.textContent = recording ? '⏹️ Stop Recording' : '🎤 Start Recording';
        domElements.recordBtn.classList.toggle('recording', recording);
        domElements.recordBtn.style.backgroundColor = recording ? '#f44336' : '';
    }
    if (domElements.recordingStatus) {
        domElements.recordingStatus.textContent = recording ? '🔴 Recording...' : '';
        domElements.recordingStatus.classList.toggle('active', recording);
    }
}

function updateProcessingUI(processing) {
    if (domElements.recordingStatus) {
        domElements.recordingStatus.textContent = processing ? '⏳ Processing...' : '';
        domElements.recordingStatus.classList.toggle('processing', processing);
    }
}

function showLoading(loading) {
    if (domElements.loadingIndicator) {
        domElements.loadingIndicator.style.display = loading ? 'block' : 'none';
    }
    if (domElements.sendBtn) {
        domElements.sendBtn.disabled = loading;
        domElements.sendBtn.textContent = loading ? '⏳ Processing...' : 'Send Query';
    }
}

function clearResults() {
    if (domElements.responseContent) domElements.responseContent.innerHTML = '<p class="placeholder-text">Your enhanced search results will appear here...</p>';
    if (domElements.pipelineInfo) domElements.pipelineInfo.innerHTML = '<p class="placeholder-text">Pipeline processing information will appear here...</p>';
    if (domElements.markdownContent) domElements.markdownContent.innerHTML = '<p class="placeholder-text">Markdown report will appear here...</p>';
    if (domElements.citationsContent) domElements.citationsContent.innerHTML = '<p class="placeholder-text">Source citations will appear here...</p>';
}

function displayError(error) {
    if (domElements.responseContent) {
        domElements.responseContent.innerHTML = `
            <div class="error-message">
                <h3>❌ Error</h3>
                <p>${error}</p>
            </div>
        `;
    }
}

// Status update functions
function updateRAGStatus(status) {
    if (domElements.ragStatus) {
        domElements.ragStatus.textContent = status;
    }
}

function updateVoiceStatus(status) {
    if (domElements.voiceStatus) {
        domElements.voiceStatus.textContent = status;
    }
}

function updateModelsStatus(status) {
    if (domElements.modelsStatus) {
        domElements.modelsStatus.textContent = status;
    }
}

// Show notification
function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Global error handler
window.addEventListener('error', function(event) {
    console.error('❌ Global error:', event.error);
    showNotification('An unexpected error occurred: ' + event.error.message, 'error');
});

console.log('🌾 IndicAgri Bot JavaScript loaded successfully!');
