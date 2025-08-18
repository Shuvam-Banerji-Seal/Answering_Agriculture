# Agriculture Bot Searcher - Complete Installation Guide

## Overview

This repository provides a complete agriculture chatbot with both text and voice input capabilities. The system integrates:

- **Text-based search and chat** using Ollama and gemma3:1b model
- **Voice transcription** supporting Indian languages (Hindi, Marathi, etc.) to English
- **Web-based interface** for easy interaction
- **Robust fallback** - text functionality works even if voice setup fails

## Quick Start

### 1. One-Command Installation

```bash
# Clone the repository (if not already done)
git clone https://github.com/Shuvam-Banerji-Seal/Answering_Agriculture.git
cd Answering_Agriculture

# Run the complete installation script
./install_agri_bot.sh
```

### 2. Start the Application

```bash
# Use the startup script (recommended)
./start_agri_bot.sh

# Or manually activate and run
source agri_bot_env/bin/activate
cd agri_bot_searcher
python3 src/voice_web_ui.py  # With voice support
# OR
python3 src/web_ui.py        # Text only
```

### 3. Verify Installation

```bash
# Check if everything is working
python3 verify_setup.py
```

## What the Installation Script Does

### 🔧 System Setup
- ✅ Checks system requirements (Python 3.8+, pip, git, curl)
- ✅ Creates isolated Python virtual environment
- ✅ Installs and configures all dependencies

### 🤖 AI Models & Services
- ✅ Installs and configures Ollama
- ✅ Downloads gemma3:1b model for text generation
- ✅ Sets up NeMo toolkit for speech recognition
- ✅ Configures IndicTrans2 for Indian language support

### 🎙️ Voice Capabilities
- ✅ Installs speech-to-text dependencies
- ✅ Configures multiple transcription engines:
  - Conformer models (offline)
  - NeMo ASR models
  - SarvamAI API (optional)
  - IndicTrans2 for translation

### 🌐 Web Interface
- ✅ Sets up Flask-based web UI
- ✅ Configures both text and voice input interfaces
- ✅ Enables real-time audio recording and processing

### 🛡️ Robustness Features
- ✅ **Graceful degradation**: If voice setup fails, text mode still works
- ✅ **Smart detection**: Automatically detects available capabilities
- ✅ **Error handling**: Continues installation even if optional components fail
- ✅ **Environment management**: Proper isolation and configuration

## Manual Installation (Alternative)

If you prefer manual control or the automated script fails:

### 1. Prerequisites

```bash
# Update system packages
sudo apt update
sudo apt install python3 python3-pip python3-venv git curl build-essential

# For audio processing (optional)
sudo apt install portaudio19-dev python3-pyaudio
```

### 2. Python Environment

```bash
cd Answering_Agriculture
python3 -m venv agri_bot_env
source agri_bot_env/bin/activate
pip install --upgrade pip setuptools wheel
```

### 3. Core Dependencies

```bash
# Install core requirements
pip install -r agri_bot_searcher/requirements_complete.txt

# Or install minimal requirements
pip install flask flask-cors requests duckduckgo-search pyyaml beautifulsoup4
```

### 4. Voice Dependencies (Optional)

```bash
# For voice functionality
pip install torch torchaudio transformers nemo-toolkit[asr]
pip install librosa soundfile indictrans[cpu]

# Optional: SarvamAI for enhanced voice processing
pip install sarvam-ai
```

### 5. Ollama Setup

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve &

# Download model
ollama pull gemma3:1b
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Optional: Hugging Face token for advanced models
HUGGINGFACE_TOKEN=your_token_here

# Optional: SarvamAI API key for enhanced voice transcription
SARVAM_API_KEY=your_api_key_here

# Voice settings
VOICE_ENABLED=true
DEFAULT_VOICE_ENGINE=conformer

# Ollama configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma3:1b

# Web UI settings
WEB_HOST=0.0.0.0
WEB_PORT=5000
```

## Usage

### Text-Only Mode

```bash
# Activate environment
source agri_bot_env/bin/activate
cd agri_bot_searcher

# Start text-only interface
python3 src/web_ui.py
```

Open http://localhost:5000 in your browser.

### Voice + Text Mode

```bash
# Activate environment
source agri_bot_env/bin/activate
cd agri_bot_searcher

# Start voice-enabled interface
python3 src/voice_web_ui.py
```

Open http://localhost:5000 in your browser. You'll see both text input and voice recording options.

### Voice Features

- 🎤 **Click "Record"** to start voice input
- 🛑 **Click "Stop"** to end recording
- 🔄 **Automatic transcription** from Indian languages to English
- 📝 **Text fallback** if voice fails
- 🌍 **Multi-language support**: Hindi, Marathi, Bengali, Tamil, etc.

## Troubleshooting

### Common Issues

1. **Ollama not starting**
   ```bash
   # Check if port 11434 is free
   sudo netstat -tlnp | grep :11434
   
   # Restart ollama
   pkill ollama
   ollama serve &
   ```

2. **Voice transcription errors**
   ```bash
   # Test audio device access
   python3 -c "import pyaudio; print('Audio OK')"
   
   # Check microphone permissions
   # Ensure browser has microphone access
   ```

3. **Missing dependencies**
   ```bash
   # Reinstall with complete requirements
   pip install -r agri_bot_searcher/requirements_complete.txt
   
   # Or check specific missing packages
   python3 verify_setup.py
   ```

4. **Port conflicts**
   ```bash
   # Use different port
   export WEB_PORT=5001
   python3 src/voice_web_ui.py
   ```

### Verification Commands

```bash
# Check installation status
python3 verify_setup.py

# Test individual components
python3 -c "import torch; print('PyTorch OK')"
python3 -c "from transformers import pipeline; print('Transformers OK')"
ollama list
curl http://localhost:11434/api/version
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Interface                        │
│  ┌─────────────────┐    ┌─────────────────────────────┐ │
│  │   Text Input    │    │      Voice Input            │ │
│  │   (Direct)      │    │  (Audio → Transcription)   │ │
│  └─────────────────┘    └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│               Agriculture Chatbot                       │
│  ┌─────────────────┐    ┌─────────────────────────────┐ │
│  │  Query Parser   │    │     Search Engine           │ │
│  │  & Processor    │    │   (DuckDuckGo + Custom)     │ │
│  └─────────────────┘    └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                 Ollama + gemma3:1b                      │
│          (Text Generation & Response)                   │
└─────────────────────────────────────────────────────────┘
```

## Development

### Adding New Voice Engines

1. Extend `VoiceTranscription` class in `src/voice_transcription.py`
2. Add new engine configuration in environment
3. Update the voice UI to support new engine

### Customizing Search

1. Modify search logic in `src/agriculture_chatbot.py`
2. Add new data sources or APIs
3. Customize response formatting

## Support

- **Issues**: Open GitHub issues for bugs or feature requests
- **Documentation**: Check individual module README files
- **Logs**: Application logs available in console output

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🎯 Goal**: Provide accessible agriculture information through both text and voice interfaces, supporting multiple Indian languages and ensuring robust fallback mechanisms.
