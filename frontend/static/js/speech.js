// IndicAgri Speech Processing Module

class SpeechManager {
    constructor() {
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.currentLanguage = 'hi-IN';
        this.initializeSpeechRecognition();
    }

    initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = this.currentLanguage;

            this.recognition.onstart = () => this.onSpeechStart();
            this.recognition.onresult = (event) => this.onSpeechResult(event);
            this.recognition.onerror = (event) => this.onSpeechError(event);
            this.recognition.onend = () => this.onSpeechEnd();
        }
    }

    startListening() {
        if (!this.recognition) {
            this.showError('आपका ब्राउज़र वॉयस इनपुट का समर्थन नहीं करता');
            return false;
        }

        if (this.isListening) {
            this.stopListening();
            return false;
        }

        try {
            this.recognition.start();
            return true;
        } catch (error) {
            this.showError('वॉयस इनपुट शुरू नहीं हो सका');
            return false;
        }
    }

    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
    }

    onSpeechStart() {
        this.isListening = true;
        this.updateVoiceButtonState('listening');
        console.log('Speech recognition started');
    }

    onSpeechResult(event) {
        const result = event.results[0].transcript;
        const confidence = event.results.confidence;
        
        console.log(`Speech result: "${result}" (confidence: ${confidence})`);
        
        if (confidence > 0.7) {
            this.onSpeechRecognized(result);
        } else {
            this.showError('आवाज़ स्पष्ट नहीं सुनाई दी, कृपया दोबारा कोशिश करें');
        }
    }

    onSpeechError(event) {
        console.error('Speech recognition error:', event.error);
        
        let errorMessage = 'वॉयस इनपुट में त्रुटि हुई';
        
        switch (event.error) {
            case 'no-speech':
                errorMessage = 'कोई आवाज़ नहीं सुनाई दी, कृपया दोबारा कोशिश करें';
                break;
            case 'audio-capture':
                errorMessage = 'माइक्रोफ़ोन एक्सेस नहीं मिला';
                break;
            case 'not-allowed':
                errorMessage = 'माइक्रोफ़ोन की अनुमति दें और दोबारा कोशिश करें';
                break;
            case 'network':
                errorMessage = 'इंटरनेट कनेक्शन की जांच करें';
                break;
        }
        
        this.showError(errorMessage);
    }

    onSpeechEnd() {
        this.isListening = false;
        this.updateVoiceButtonState('idle');
        console.log('Speech recognition ended');
    }

    onSpeechRecognized(text) {
        // Dispatch custom event with recognized text
        const event = new CustomEvent('speechRecognized', {
            detail: { text: text, language: this.currentLanguage }
        });
        document.dispatchEvent(event);
    }

    speak(text, language = 'hi-IN') {
        if (!this.synthesis) {
            console.warn('Speech synthesis not supported');
            return;
        }

        // Cancel any ongoing speech
        this.synthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = language;
        utterance.rate = 0.9;
        utterance.pitch = 1;
        utterance.volume = 1;

        // Try to find a voice for the selected language
        const voices = this.synthesis.getVoices();
        const voice = voices.find(v => v.lang.startsWith(language.split('-')[0]));
        if (voice) {
            utterance.voice = voice;
        }

        utterance.onstart = () => console.log('Speech synthesis started');
        utterance.onend = () => console.log('Speech synthesis ended');
        utterance.onerror = (event) => console.error('Speech synthesis error:', event);

        this.synthesis.speak(utterance);
    }

    setLanguage(languageCode) {
        this.currentLanguage = this.getFullLanguageCode(languageCode);
        if (this.recognition) {
            this.recognition.lang = this.currentLanguage;
        }
    }

    getFullLanguageCode(shortCode) {
        const languageMap = {
            'hi': 'hi-IN',
            'en': 'en-IN',
            'bn': 'bn-IN',
            'te': 'te-IN',
            'mr': 'mr-IN',
            'ta': 'ta-IN',
            'gu': 'gu-IN',
            'kn': 'kn-IN',
            'ml': 'ml-IN',
            'pa': 'pa-IN'
        };
        return languageMap[shortCode] || 'hi-IN';
    }

    updateVoiceButtonState(state) {
        const voiceBtn = document.getElementById('voiceBtn');
        const voiceIcon = voiceBtn?.querySelector('.voice-icon i');
        
        if (!voiceBtn || !voiceIcon) return;

        voiceBtn.classList.remove('listening', 'processing');
        
        switch (state) {
            case 'listening':
                voiceBtn.classList.add('listening');
                voiceIcon.className = 'fas fa-stop';
                break;
            case 'processing':
                voiceBtn.classList.add('processing');
                voiceIcon.className = 'fas fa-cog fa-spin';
                break;
            case 'idle':
            default:
                voiceIcon.className = 'fas fa-microphone';
                break;
        }
    }

    showError(message) {
        const event = new CustomEvent('speechError', {
            detail: { message: message }
        });
        document.dispatchEvent(event);
    }

    // Check if speech recognition is supported
    isSupported() {
        return !!(window.SpeechRecognition || window.webkitSpeechRecognition);
    }

    // Check if speech synthesis is supported
    isSynthesisSupported() {
        return !!(window.speechSynthesis);
    }
}

// Export for use in main app
window.SpeechManager = SpeechManager;
