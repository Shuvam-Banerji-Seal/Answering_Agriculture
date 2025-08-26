# IndicAgri Bot - Installation and Setup Guide

## Overview

IndicAgri Bot is an advanced agriculture chatbot with voice capabilities, designed specifically for Indian farmers. It combines:

- **RAG (Retrieval Augmented Generation)** system for accurate agricultural information
- **Voice transcription** in multiple Indian languages
- **Web search** capabilities for real-time information
- **Multi-agent** architecture for comprehensive responses

## Quick Installation

### 1. Clone and Install

```bash
git clone <repository-url>
cd Answering_Agriculture
chmod +x install_indicagri_bot.sh
./install_indicagri_bot.sh
```

### 2. Start the Bot

```bash
./start_indicagri_bot.sh
```

Access the web interface at: http://localhost:5000

## Installation Options

### Full Installation (Recommended)
```bash
./install_indicagri_bot.sh
```
Includes: Voice features, RAG system, web search, Ollama integration

### Lightweight Installation
```bash
./install_indicagri_bot.sh --no-voice --no-rag
```
Includes: Basic web search only

### Custom Model
```bash
./install_indicagri_bot.sh --model gemma2:2b
```
Use different Ollama model (lighter/heavier options available)

## Features

### 🎤 Voice Input
- Support for Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, and more
- Local speech recognition models (no internet required)
- Optional SarvamAI integration for enhanced accuracy

### 🧠 RAG System
- Pre-indexed agriculture knowledge base
- Semantic search for relevant information
- Embedding-based retrieval

### 🌐 Web Search
- Real-time information from agricultural websites
- Multi-agent search strategy
- DuckDuckGo integration

### 🔧 Ollama Integration
- Local LLM processing
- Privacy-focused (no data sent to external APIs)
- Multiple model options

## API Keys Setup (Optional)

### SarvamAI API Key
1. Visit [sarvam.ai](https://www.sarvam.ai/)
2. Sign up for an account
3. Navigate to API section
4. Generate API key
5. Enter in the web interface

**Benefits**: Enhanced voice transcription accuracy for Indian languages

### Hugging Face Token
1. Visit [huggingface.co](https://huggingface.co/)
2. Create account and go to Settings → Access Tokens
3. Create "Read" token
4. Enter in the web interface

**Benefits**: Access to gated models and higher rate limits

## System Requirements

- **OS**: Linux (Ubuntu 18.04+), macOS, Windows 10+
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB+ recommended
- **Storage**: 10GB free space (for models and embeddings)
- **Network**: Internet connection for initial setup

## Directory Structure

```
Answering_Agriculture/
├── install_indicagri_bot.sh          # Main installation script
├── start_indicagri_bot.sh            # Startup script
├── requirements.txt                  # Unified dependencies
├── agri_bot_searcher/               # Main application
│   ├── src/
│   │   ├── enhanced_voice_web_ui.py # Voice + Text interface
│   │   ├── enhanced_web_ui.py       # RAG + Web interface  
│   │   ├── web_ui.py               # Basic interface
│   │   └── ...
│   └── config/
└── agriculture_embeddings/          # RAG knowledge base
```

## Usage Modes

### 1. Voice + Text Mode (Full Features)
- Voice input in Indian languages
- Text chat interface
- RAG knowledge base
- Web search integration

### 2. RAG + Web Mode
- Text-only interface
- Enhanced knowledge retrieval
- Web search fallback

### 3. Basic Mode
- Simple web search interface
- Lightweight and fast

## Troubleshooting

### Common Issues

**1. Installation Fails**
```bash
# Check Python version
python3 --version

# Ensure pip is updated
pip3 install --upgrade pip
```

**2. Ollama Not Starting**
```bash
# Manual start
ollama serve

# Check if running
ps aux | grep ollama
```

**3. Voice Features Not Working**
```bash
# Install audio dependencies (Ubuntu)
sudo apt-get install libasound2-dev portaudio19-dev

# Check microphone permissions in browser
```

**4. RAG System Issues**
```bash
# Verify embeddings directory
ls -la agriculture_embeddings/

# Check if FAISS index exists
```

### Getting Help

1. Check the console output for error messages
2. Verify all dependencies are installed
3. Ensure proper file permissions
4. Check firewall settings for port 5000

## Development

### Running in Development Mode

```bash
source agri_bot_env/bin/activate
cd agri_bot_searcher
python3 src/enhanced_voice_web_ui.py --debug
```

### Adding New Features

1. Fork the repository
2. Create feature branch
3. Install development dependencies
4. Make changes and test
5. Submit pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please read the contributing guidelines and submit pull requests for any improvements.

## Support

For support and questions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review the documentation

---

**Note**: This project does not include IndicTrans due to dependency conflicts. Voice transcription uses alternative robust models for Indian language support.
