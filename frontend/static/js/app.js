// IndicAgri Main Application

class IndicAgriApp {
    constructor() {
        this.speechManager = new SpeechManager();
        this.currentLanguage = 'hi';
        this.apiBaseUrl = '/api/v1'; // Backend API endpoint
        this.isOnline = navigator.onLine;
        
        this.initializeApp();
    }

    initializeApp() {
        this.setupEventListeners();
        this.setupLanguageSelector();
        this.setupQuickActions();
        this.setupChatInterface();
        this.checkOnlineStatus();
        this.loadUserPreferences();
    }

    setupEventListeners() {
        // Voice button click
        const voiceBtn = document.getElementById('voiceBtn');
        voiceBtn?.addEventListener('click', () => this.handleVoiceInput());

        // Text input handling
        const textInput = document.querySelector('.text-input');
        const sendBtn = document.querySelector('.send-btn');
        
        textInput?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.processTextInput(textInput.value);
            }
        });

        textInput?.addEventListener('input', (e) => {
            this.toggleSendButton(e.target.value.trim().length > 0);
        });

        sendBtn?.addEventListener('click', () => {
            this.processTextInput(textInput.value);
        });

        // Chat interface
        this.setupChatEventListeners();

        // Mobile menu toggle
        const menuToggle = document.querySelector('.menu-toggle');
        menuToggle?.addEventListener('click', () => this.toggleMobileMenu());

        // Speech recognition events
        document.addEventListener('speechRecognized', (e) => {
            this.handleSpeechRecognized(e.detail.text);
        });

        document.addEventListener('speechError', (e) => {
            this.showNotification(e.detail.message, 'error');
        });

        // Online/offline status
        window.addEventListener('online', () => this.handleOnlineStatus(true));
        window.addEventListener('offline', () => this.handleOnlineStatus(false));

        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            this.closeActiveDropdowns(e);
        });
    }

    setupChatEventListeners() {
        const chatInput = document.querySelector('.chat-input input');
        const sendMessage = document.querySelector('.send-message');
        const voiceToggle = document.querySelector('.voice-toggle');
        const chatClose = document.querySelector('.chat-close');

        chatInput?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendChatMessage(chatInput.value);
            }
        });

        sendMessage?.addEventListener('click', () => {
            this.sendChatMessage(chatInput.value);
        });

        voiceToggle?.addEventListener('click', () => {
            this.handleVoiceInput();
        });

        chatClose?.addEventListener('click', () => {
            this.closeChatInterface();
        });
    }

    handleVoiceInput() {
        if (!this.speechManager.isSupported()) {
            this.showNotification('आपका ब्राउज़र वॉयस इनपुट का समर्थन नहीं करता', 'warning');
            return;
        }

        const started = this.speechManager.startListening();
        if (started) {
            this.showNotification('बोलना शुरू करें...', 'info', 3000);
        }
    }

    handleSpeechRecognized(text) {
        console.log('Processing speech input:', text);
        this.processQuery(text, 'voice');
        
        // Show recognized text briefly
        this.showNotification(`समझा गया: "${text}"`, 'success', 2000);
    }

    processTextInput(text) {
        if (!text || !text.trim()) return;
        
        this.processQuery(text.trim(), 'text');
        
        // Clear input
        const textInput = document.querySelector('.text-input');
        if (textInput) {
            textInput.value = '';
            this.toggleSendButton(false);
        }
    }

    async processQuery(query, inputType = 'text') {
        console.log(`Processing ${inputType} query:`, query);
        
        try {
            // Show loading state
            this.showLoading(true);
            
            // Open chat interface if not already open
            this.openChatInterface();
            
            // Add user message to chat
            this.addChatMessage(query, 'user');
            
            // Call backend API
            const response = await this.callBackendAPI(query, inputType);
            
            // Add bot response to chat
            this.addChatMessage(response.answer, 'bot', response.sources);
            
            // Speak response if voice input was used
            if (inputType === 'voice' && this.speechManager.isSynthesisSupported()) {
                this.speechManager.speak(response.answer, this.speechManager.currentLanguage);
            }
            
        } catch (error) {
            console.error('Error processing query:', error);
            this.handleAPIError(error);
        } finally {
            this.showLoading(false);
        }
    }

    async callBackendAPI(query, inputType) {
        if (!this.isOnline) {
            return this.getOfflineResponse(query);
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    input_type: inputType,
                    language: this.currentLanguage,
                    user_location: this.getUserLocation(),
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('Backend API error:', error);
            
            // Fallback to mock response
            return this.getMockResponse(query);
        }
    }

    getMockResponse(query) {
        // Mock responses based on query content for demo purposes
        const lowerQuery = query.toLowerCase();
        
        if (lowerQuery.includes('मौसम') || lowerQuery.includes('weather')) {
            return {
                answer: 'आज का मौसम साफ है। तापमान 25°C है। अगले 3 दिन बारिश की संभावना है। अपनी फसल को बारिश से बचाने के लिए उचित व्यवस्था करें।',
                sources: [
                    { title: 'IMD Weather Report', url: '#', relevance: 0.95 }
                ],
                confidence: 0.89
            };
        } else if (lowerQuery.includes('धान') || lowerQuery.includes('rice')) {
            return {
                answer: 'धान की फसल में पीले पत्ते आमतौर पर नाइट्रोजन की कमी या पानी की अधिकता के कारण होते हैं। मिट्टी की जांच कराएं और उचित मात्रा में यूरिया का प्रयोग करें। सिंचाई में संयम बरतें।',
                sources: [
                    { title: 'ICAR Rice Cultivation Guide', url: '#', relevance: 0.92 }
                ],
                confidence: 0.94
            };
        } else if (lowerQuery.includes('कीमत') || lowerQuery.includes('price')) {
            return {
                answer: 'आज के बाज़ार भाव: गेहूं ₹2,150 प्रति क्विंटल, धान ₹1,980 प्रति क्विंटल, मक्का ₹1,850 प्रति क्विंटल। अगले सप्ताह कीमतों में मामूली वृद्धि की संभावना है।',
                sources: [
                    { title: 'APMC Market Prices', url: '#', relevance: 0.96 }
                ],
                confidence: 0.91
            };
        } else {
            return {
                answer: 'आपका प्रश्न बहुत अच्छा है। हमारे कृषि विशेषज्ञ इसका विस्तृत उत्तर तैयार कर रहे हैं। आप और भी कृषि संबंधी प्रश्न पूछ सकते हैं।',
                sources: [],
                confidence: 0.75
            };
        }
    }

    getOfflineResponse(query) {
        return {
            answer: 'आप ऑफ़लाइन हैं। कुछ बुनियादी जानकारी उपलब्ध है, लेकिन नवीनतम डेटा के लिए कृपया इंटरनेट कनेक्शन की जांच करें।',
            sources: [],
            confidence: 0.5
        };
    }

    setupLanguageSelector() {
        const languageBtn = document.querySelector('.language-btn');
        const languageSelector = document.querySelector('.language-selector');
        const languageOptions = document.querySelectorAll('.language-option');

        languageBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            languageSelector?.classList.toggle('active');
        });

        languageOptions.forEach(option => {
            option.addEventListener('click', () => {
                const lang = option.dataset.lang;
                const langText = option.textContent;
                
                this.changeLanguage(lang, langText);
                languageSelector?.classList.remove('active');
            });
        });
    }

    changeLanguage(langCode, langText) {
        this.currentLanguage = langCode;
        
        // Update button text
        const languageBtn = document.querySelector('.language-btn span');
        if (languageBtn) {
            languageBtn.textContent = langText;
        }

        // Update speech recognition language
        this.speechManager.setLanguage(langCode);

        // Update active state
        document.querySelectorAll('.language-option').forEach(option => {
            option.classList.remove('active');
            if (option.dataset.lang === langCode) {
                option.classList.add('active');
            }
        });

        // Save preference
        localStorage.setItem('indicagri_language', langCode);
        
        this.showNotification(`भाषा बदलकर ${langText} की गई`, 'success', 2000);
    }

    setupQuickActions() {
        const quickBtns = document.querySelectorAll('.quick-btn');
        
        quickBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.dataset.action;
                this.handleQuickAction(action);
            });
        });
    }

    handleQuickAction(action) {
        const queries = {
            'weather': 'आज का मौसम कैसा है?',
            'crop-disease': 'मेरी फसल में बीमारी के लक्षण दिख रहे हैं',
            'market-price': 'आज के बाज़ार भाव क्या हैं?',
            'schemes': 'कृषि योजनाओं की जानकारी दें'
        };
        
        const query = queries[action];
        if (query) {
            this.processQuery(query, 'quick-action');
        }
    }

    openChatInterface() {
        const chatInterface = document.getElementById('chatInterface');
        if (chatInterface) {
            chatInterface.classList.add('active');
            
            // Focus on chat input
            setTimeout(() => {
                const chatInput = document.querySelector('.chat-input input');
                chatInput?.focus();
            }, 300);
        }
    }

    closeChatInterface() {
        const chatInterface = document.getElementById('chatInterface');
        chatInterface?.classList.remove('active');
    }

    setupChatInterface() {
        // Initialize with welcome message
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages && chatMessages.children.length === 1) {
            // Only welcome message exists, add some quick suggestions
            this.addQuickSuggestions();
        }
    }

    addQuickSuggestions() {
        const suggestions = [
            'मौसम की जानकारी',
            'फसल की बीमारी',
            'बाज़ार की कीमतें',
            'सरकारी योजनाएं'
        ];

        const suggestionDiv = document.createElement('div');
        suggestionDiv.className = 'chat-suggestions';
        suggestionDiv.innerHTML = `
            <p>आप इन विषयों पर प्रश्न पूछ सकते हैं:</p>
            <div class="suggestion-buttons">
                ${suggestions.map(suggestion => 
                    `<button class="suggestion-btn" data-suggestion="${suggestion}">${suggestion}</button>`
                ).join('')}
            </div>
        `;

        // Add styles for suggestions
        suggestionDiv.style.cssText = `
            padding: var(--spacing-md);
            margin: var(--spacing-sm) 0;
            background: var(--light-gray);
            border-radius: var(--radius-lg);
        `;

        const chatMessages = document.getElementById('chatMessages');
        chatMessages?.appendChild(suggestionDiv);

        // Add event listeners to suggestion buttons
        suggestionDiv.querySelectorAll('.suggestion-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const suggestion = btn.dataset.suggestion;
                this.processQuery(suggestion, 'suggestion');
                suggestionDiv.remove(); // Remove suggestions after use
            });
            
            // Style suggestion buttons
            btn.style.cssText = `
                margin: var(--spacing-xs);
                padding: var(--spacing-sm) var(--spacing-md);
                background: var(--primary-green);
                color: var(--white);
                border: none;
                border-radius: var(--radius-md);
                cursor: pointer;
                font-size: 0.875rem;
                transition: background-color 0.2s ease;
            `;
            
            btn.addEventListener('mouseenter', () => {
                btn.style.backgroundColor = 'var(--primary-green-dark)';
            });
            
            btn.addEventListener('mouseleave', () => {
                btn.style.backgroundColor = 'var(--primary-green)';
            });
        });
    }

    addChatMessage(message, sender = 'bot', sources = []) {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = sender === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        let sourcesHtml = '';
        if (sources && sources.length > 0) {
            sourcesHtml = `
                <div class="message-sources">
                    <small>स्रोत: ${sources.map(source => 
                        `<a href="${source.url}" target="_blank">${source.title}</a>`
                    ).join(', ')}</small>
                </div>
            `;
        }

        contentDiv.innerHTML = `
            <p>${message}</p>
            ${sourcesHtml}
            <div class="message-time">${this.getCurrentTime()}</div>
        `;

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Add typing animation for bot messages
        if (sender === 'bot') {
            this.animateTyping(contentDiv.querySelector('p'));
        }
    }

    animateTyping(element) {
        const text = element.textContent;
        element.textContent = '';
        
        let i = 0;
        const typeInterval = setInterval(() => {
            element.textContent += text[i];
            i++;
            
            if (i >= text.length) {
                clearInterval(typeInterval);
            }
        }, 30);
    }

    sendChatMessage(message) {
        if (!message || !message.trim()) return;

        this.processQuery(message.trim(), 'chat');

        // Clear input
        const chatInput = document.querySelector('.chat-input input');
        if (chatInput) {
            chatInput.value = '';
        }
    }

    toggleSendButton(enabled) {
        const sendBtn = document.querySelector('.send-btn');
        if (sendBtn) {
            sendBtn.disabled = !enabled;
            sendBtn.style.opacity = enabled ? '1' : '0.5';
        }
    }

    showLoading(show = true) {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            if (show) {
                loadingOverlay.classList.add('active');
            } else {
                loadingOverlay.classList.remove('active');
            }
        }
    }

    showNotification(message, type = 'info', duration = 5000) {
        // Remove existing notifications
        document.querySelectorAll('.app-notification').forEach(n => n.remove());

        const notification = document.createElement('div');
        notification.className = `app-notification notification-${type}`;
        
        const colors = {
            success: '#4CAF50',
            error: '#F44336',
            warning: '#FF9800',
            info: '#2196F3'
        };

        notification.innerHTML = `
            <div class="notification-content">
                <span>${message}</span>
                <button class="notification-close" aria-label="Close">&times;</button>
            </div>
        `;

        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            background: colors[type] || colors.info,
            color: 'white',
            padding: '16px',
            borderRadius: '8px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            zIndex: '10000',
            maxWidth: '400px',
            fontSize: '14px',
            animation: 'slideInRight 0.3s ease-out'
        });

        document.body.appendChild(notification);

        // Auto remove
        const autoRemove = setTimeout(() => {
            notification.remove();
        }, duration);

        // Close button functionality
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn?.addEventListener('click', () => {
            clearTimeout(autoRemove);
            notification.remove();
        });
    }

    toggleMobileMenu() {
        const menuToggle = document.querySelector('.menu-toggle');
        const headerActions = document.querySelector('.header-actions');
        
        menuToggle?.classList.toggle('active');
        headerActions?.classList.toggle('mobile-active');
    }

    closeActiveDropdowns(event) {
        // Close language dropdown if clicked outside
        const languageSelector = document.querySelector('.language-selector');
        if (languageSelector && !languageSelector.contains(event.target)) {
            languageSelector.classList.remove('active');
        }
    }

    handleOnlineStatus(isOnline) {
        this.isOnline = isOnline;
        
        const message = isOnline ? 
            'इंटरनेट कनेक्शन बहाल हो गया' : 
            'आप ऑफ़लाइन हैं - सीमित सुविधाएं उपलब्ध हैं';
        
        const type = isOnline ? 'success' : 'warning';
        this.showNotification(message, type, 3000);
    }

    checkOnlineStatus() {
        this.isOnline = navigator.onLine;
    }

    getUserLocation() {
        // Try to get user location from localStorage or browser
        return localStorage.getItem('user_location') || 'भारत';
    }

    getCurrentTime() {
        return new Date().toLocaleTimeString('hi-IN', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }

    loadUserPreferences() {
        // Load saved language preference
        const savedLanguage = localStorage.getItem('indicagri_language');
        if (savedLanguage) {
            const languageOption = document.querySelector(`[data-lang="${savedLanguage}"]`);
            if (languageOption) {
                const langText = languageOption.textContent;
                this.changeLanguage(savedLanguage, langText);
            }
        }
    }

    handleAPIError(error) {
        let message = 'कुछ तकनीकी समस्या हुई है। कृपया दोबारा कोशिश करें।';
        
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            message = 'सर्वर से जुड़ाव में समस्या है। कृपया अपना इंटरनेट कनेक्शन जांचें।';
        } else if (error.message.includes('500')) {
            message = 'सर्वर में कुछ समस्या है। हम इसे ठीक करने की कोशिश कर रहे हैं।';
        }
        
        this.addChatMessage(message, 'bot');
        this.showNotification(message, 'error');
    }
}

// Add CSS animation for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.indicAgriApp = new IndicAgriApp();
});

// Register service worker for PWA
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
            .then((registration) => {
                console.log('SW registered: ', registration);
            })
            .catch((registrationError) => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
