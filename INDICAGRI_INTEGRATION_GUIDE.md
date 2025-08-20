# IndicAgri Bot - Voice & Text Integration Guide

## Overview

IndicAgri Bot is an enhanced agricultural assistant that combines:

1. **Voice Transcription**: Multi-language voice input using AI4Bharat models and IndicTrans2
2. **Text Search**: Web search capabilities for real-time agricultural information
3. **Multi-Agent Processing**: Multiple Ollama agents for comprehensive responses
4. **Enhanced RAG**: Optional enhanced retrieval-augmented generation

## Features

### Voice Capabilities
- **22+ Indian Languages**: Support for all major Indian languages including Hindi, Marathi, Bengali, Tamil, Telugu, Gujarati, Kannada, Malayalam, Punjabi, and more
- **Dual Transcription Modes**: 
  - Local AI4Bharat Conformer models for offline processing
  - SarvamAI cloud service for enhanced accuracy
- **Real-time Translation**: Automatic translation to English using IndicTrans2
- **Audio Format Support**: Automatic conversion to mono 16kHz WAV format

### Text Processing
- **Multi-Agent Search**: Deploys multiple specialized agents for comprehensive responses
- **Real-time Web Search**: Live information from agricultural websites and resources
- **Citation Support**: Inline citations for all information sources
- **Agriculture-Specific Enhancement**: Specialized query enhancement for farming topics

## Installation

### Quick Start
```bash
# Make installation script executable
chmod +x install_agri_bot.sh

# Run complete installation
./install_agri_bot.sh

# Start IndicAgri Bot
./start_agri_bot.sh
```

### Manual Installation Steps

1. **System Requirements**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-venv python3-pip git curl ffmpeg

   # CentOS/RHEL
   sudo yum install python3 python3-venv python3-pip git curl ffmpeg
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv agri_bot_env
   source agri_bot_env/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   cd agri_bot_searcher
   pip install -r requirements_indicagri_voice.txt
   ```

4. **Install Ollama**
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ollama serve &
   ollama pull gemma3:1b
   ollama pull gemma3:27b  # Optional but recommended
   ```

5. **Setup agri_bot Voice Components**
   ```bash
   cd ../agri_bot
   bash install.sh
   ```

## Usage

### Starting the Application

1. **Automatic Start** (Recommended)
   ```bash
   ./start_agri_bot.sh
   ```

2. **Manual Start**
   ```bash
   source agri_bot_env/bin/activate
   cd agri_bot_searcher
   python3 src/enhanced_voice_web_ui.py
   ```

3. **Open Browser**
   - Navigate to: `http://localhost:5000`
   - The IndicAgri Bot interface will load

### Using Voice Input

1. **Select Language**: Choose from 22+ supported Indian languages
2. **Configure Settings**:
   - Use Local Model: Enable for offline AI4Bharat processing
   - SarvamAI: Disable local model and provide API key for cloud processing
   - Hugging Face Token: Required for some local models

3. **Record Voice**:
   - Click the microphone button to start recording
   - Speak your agricultural question clearly
   - Click stop to end recording
   - Wait for transcription and translation

4. **Review Results**:
   - Original transcription appears in your selected language
   - English translation appears automatically
   - Translation is auto-filled into the query box

### Using Text Input

1. **Direct Text**: Type your question directly in the query box
2. **Voice-to-Text**: Use voice input which auto-fills the text box
3. **Send Query**: Click "Send Query" to get comprehensive responses

## Language Support

### Supported Languages with Script Codes

| Language | Script | Code |
|----------|---------|------|
| Assamese | Bengali | asm_Beng |
| Bengali | Bengali | ben_Beng |
| Bodo | Devanagari | brx_Deva |
| Dogri | Devanagari | doi_Deva |
| Gujarati | Gujarati | guj_Gujr |
| Hindi | Devanagari | hin_Deva |
| Kannada | Kannada | kan_Knda |
| Konkani | Devanagari | gom_Deva |
| Kashmiri | Arabic/Devanagari | kas_Arab/kas_Deva |
| Maithili | Devanagari | mai_Deva |
| Malayalam | Malayalam | mal_Mlym |
| Manipuri | Bengali/Meitei | mni_Beng/mni_Mtei |
| Marathi | Devanagari | mar_Deva |
| Nepali | Devanagari | npi_Deva |
| Odia | Odia | ory_Orya |
| Punjabi | Gurmukhi | pan_Guru |
| Sanskrit | Devanagari | san_Deva |
| Santali | Ol Chiki | sat_Olck |
| Sindhi | Arabic/Devanagari | snd_Arab/snd_Deva |
| Urdu | Arabic | urd_Arab |
| English | Latin | eng_Latn |

## Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Voice Settings
VOICE_ENABLED=true
DEFAULT_VOICE_ENGINE=conformer

# API Keys (Optional)
SARVAM_API_KEY=your_sarvam_api_key
HUGGINGFACE_TOKEN=your_hf_token

# Ollama Settings
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma3:1b

# Web Interface
WEB_HOST=0.0.0.0
WEB_PORT=5000
```

### Voice Transcription Options

1. **Local Processing (Recommended)**:
   - Uses AI4Bharat Conformer models
   - Offline processing
   - Requires conformer.nemo model file
   - Better privacy

2. **Cloud Processing (SarvamAI)**:
   - Requires API key
   - Online processing
   - Higher accuracy for some languages
   - Usage costs apply

## API Endpoints

### Voice Transcription
```bash
POST /transcribe
Content-Type: multipart/form-data

Parameters:
- audio: WAV file (auto-converted to mono 16kHz)
- language: Language code (e.g., hin_Deva)
- use_local_model: true/false
- api_key: SarvamAI API key (if using cloud)
- hf_token: Hugging Face token (if needed)
```

### Chat Query
```bash
POST /chat
Content-Type: application/json

{
  "query": "Your agricultural question",
  "num_agents": 2,
  "base_port": 11434
}
```

### Health Check
```bash
GET /health
```

## Troubleshooting

### Common Issues

1. **Voice Recording Not Working**
   - Check microphone permissions in browser
   - Ensure HTTPS or localhost usage
   - Verify microphone is not in use by other applications

2. **Transcription Errors**
   - Check if agri_bot modules are installed correctly
   - Verify Hugging Face token if required
   - Ensure sufficient disk space for models

3. **Ollama Connection Issues**
   - Verify Ollama service is running: `ollama list`
   - Check port availability: `netstat -an | grep 11434`
   - Restart Ollama: `pkill ollama; ollama serve &`

4. **Model Loading Errors**
   - Ensure sufficient RAM (8GB+ recommended)
   - Check if models are downloaded: `ollama list`
   - Download missing models: `ollama pull gemma3:1b`

### Performance Optimization

1. **For Better Voice Performance**:
   - Use GPU if available
   - Close unnecessary applications
   - Use local models for faster processing

2. **For Better Search Performance**:
   - Increase number of agents (2-4 recommended)
   - Use faster Ollama models if available
   - Ensure stable internet connection

## Development

### Project Structure
```
IndicAgri/
├── agri_bot/                          # Voice transcription module
│   ├── new_bot.py                     # Main transcription logic
│   ├── utility.py                     # Audio processing utilities
│   ├── load.py                        # Model loading functions
│   └── install.sh                     # Voice dependencies installer
├── agri_bot_searcher/                 # Main application
│   ├── src/
│   │   ├── enhanced_voice_web_ui.py   # Main web interface
│   │   ├── indicagri_voice_integration.py  # Voice integration
│   │   ├── agriculture_chatbot.py     # Multi-agent chatbot
│   │   └── ...
│   └── requirements_indicagri_voice.txt
├── install_agri_bot.sh               # Complete installer
├── start_agri_bot.sh                 # Startup script
└── test_indicagri_integration.py     # Integration tests
```

### Testing
```bash
# Run integration tests
python3 test_indicagri_integration.py

# Test voice transcription specifically
cd agri_bot_searcher/src
python3 indicagri_voice_integration.py --audio test.wav --language hin_Deva
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in the terminal where the application was started
3. Verify all dependencies are installed correctly
4. Test with the integration test script

## License

This project integrates multiple components with their respective licenses. Please refer to individual component licenses for specific terms.
