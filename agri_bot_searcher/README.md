# Agriculture Bot Searcher 🌾🎤

A sophisticated multi-agent chatbot system with **voice input capabilities** that deploys specialized Ollama agents to search the internet and provide comprehensive answers to agricultural queries with inline citations. Now supports **Indian language voice input** with automatic English translation!

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Voice Support](https://img.shields.io/badge/voice-10%20Indian%20languages-green.svg)](https://github.com/AI4Bharat)

## ✨ Features

### 🎤 Voice Input (NEW!)
- **🗣️ Indian Language Support**: Hindi, Marathi, Bengali, Telugu, Tamil, Gujarati, Kannada, Malayalam, Punjabi, Odia
- **🔄 Automatic Translation**: Speech-to-text with English translation using AI4Bharat models
- **🌐 Multiple Backends**: SarvamAI, NeMo Conformer, and IndicTrans2 integration
- **📱 Web Interface**: Real-time voice recording and file upload support

### 🤖 Advanced Agriculture AI
- **🤖 Multi-Agent System**: Deploys specialized agents with different agricultural expertise
- **🔍 Real-time Web Search**: Internet search integration for current information
- **📚 Inline Citations**: Automatic citation generation with source links
- **🌱 Agriculture-Focused**: Enhanced queries and domain-specific optimization
- **⚡ Dual Answer Modes**: Choose between detailed analysis or concise practical advice
- **🛡️ Robust Error Handling**: Graceful handling of agent failures and timeouts

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/download) installed and running
- Internet connection for web search
- **For Voice Features**: CUDA-compatible GPU (recommended), microphone access

### Installation Options

#### Option 1: Voice-Enabled Setup (Recommended)
```bash
# Navigate to the project directory
cd agri_bot_searcher

# Run the voice-enabled setup
./start_voice_system.sh
```

#### Option 2: Manual Installation
```bash
# Install voice-enabled dependencies
pip install -r requirements_voice.txt

# Install additional dependencies
pip install git+https://github.com/AI4Bharat/IndicTrans2.git
pip install nemo-toolkit[asr]

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

#### Option 3: Text-Only Setup
```bash
# Original installation method
./install.sh
pip install -r requirements.txt
```

### Usage

#### 🎤 Voice-Enabled Web Interface (NEW!)
```bash
# Start the voice-enabled interface
python src/voice_web_ui.py

# Open browser: http://localhost:5000
# - Click microphone to record voice in Indian languages
# - Upload audio files for transcription
# - Use text input as before
```

#### 🌐 Original Web Interface
```bash
# Start the web interface
python src/web_ui.py

# Open browser: http://localhost:5000
```

#### Command Line
```bash
# Detailed analysis
python src/agriculture_chatbot.py --query "How to treat bacterial blight in rice?" --agents 2

# Concise answer
python src/agriculture_chatbot.py --query "Best fertilizer for wheat" --exact

# Interactive mode
python tests/test_agriculture_chatbot.py

# Test voice transcription
python demo_voice_integration.py
```

## 🎤 Voice Input Configuration

### Supported Languages
| Language | Code | Script | Status |
|----------|------|---------|--------|
| Hindi | `hi` | Devanagari | ✅ |
| Marathi | `mr` | Devanagari | ✅ |
| Bengali | `bn` | Bengali | ✅ |
| Telugu | `te` | Telugu | ✅ |
| Tamil | `ta` | Tamil | ✅ |
| Gujarati | `gu` | Gujarati | ✅ |
| Kannada | `kn` | Kannada | ✅ |
| Malayalam | `ml` | Malayalam | ✅ |
| Punjabi | `pa` | Gurmukhi | ✅ |
| Odia | `or` | Odia | ✅ |

### Voice Setup Options

#### 1. SarvamAI (Recommended)
```bash
# Get API key from https://sarvam.ai/
export SARVAM_API_KEY="your_api_key"

# Advantages:
# - High accuracy (85-95%)
# - Fast processing (2-5 seconds)
# - All Indian languages supported
# - Direct English output
```

#### 2. AI4Bharat Models (Free)
```bash
# Download Conformer model
wget -O models/conformer.nemo "https://storage.googleapis.com/conformer_models/conformer.nemo"

# Advantages:
# - Free and open source
# - Local processing (privacy)
# - Customizable
# - Works offline
```

#### 3. Hybrid Mode (Best)
```bash
# Use both - SarvamAI as primary, Conformer as fallback
# Automatically configured when both are available
```

### Environment Setup
```bash
# Create .env file
cat > .env << EOL
# SarvamAI API Key (optional but recommended)
SARVAM_API_KEY=your_sarvam_api_key

# HuggingFace Token (for model downloads)
HUGGINGFACE_TOKEN=your_hf_token

# Model paths
CONFORMER_MODEL_PATH=./models/conformer.nemo

# Device settings
TORCH_DEVICE=cuda  # or cpu
EOL
```

#### Web Interface (Recommended)
```bash
# Launch the web UI
./start_web_ui.sh

# Or manually
python src/web_ui.py
```

Then open http://localhost:5000 in your browser for the full-featured interface with:
- **🔧 Configurable Parameters**: Ollama port, number of agents, search count
- **🎯 Answer Modes**: Toggle between detailed analysis and concise answers  
- **📊 Real-time Status**: Live system monitoring and agent availability
- **📈 Performance Stats**: Response time, citations, and agent usage metrics

# Concise answer
python src/agriculture_chatbot.py --query "How to treat bacterial blight in rice?" --agents 2 --exact
```

#### Interactive Mode
```bash
python tests/test_agriculture_chatbot.py --interactive
```

#### Python API
```python
import sys
sys.path.append('src')
from agriculture_chatbot import AgricultureChatbot

chatbot = AgricultureChatbot(base_port=11434, num_agents=3)
result = chatbot.answer_query("Best rice cultivation practices?", exact_answer=True)
print(result["answer"])
```

## 📁 Project Structure

```
agri_bot_searcher/
├── src/
│   └── agriculture_chatbot.py      # Main chatbot implementation
├── tests/
│   ├── test_agriculture_chatbot.py # Test script and interactive mode
│   └── demo_agriculture_modes.py   # Mode comparison demo
├── scripts/
│   └── setup_agriculture_chatbot.py # Setup and installation helper
├── docs/
│   ├── README_AGRICULTURE_CHATBOT.md # Comprehensive documentation
│   └── AGRICULTURE_CHATBOT_SUMMARY.md # Implementation summary
├── requirements.txt                # Python dependencies
├── install.sh                     # Installation script
├── docker-compose.yml             # Docker deployment
├── Dockerfile                     # Docker container definition
└── README.md                      # This file
```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)
```bash
docker-compose up -d
```

### Manual Docker Build
```bash
docker build -t agri-bot-searcher .
docker run -p 8000:8000 agri-bot-searcher
```

## 🎯 Agent Specializations

The system includes specialized agents for different agricultural domains:

1. **🌾 Crop Specialist** - Cultivation practices, yield optimization
2. **🦠 Disease Expert** - Plant pathology, pest management, treatment
3. **💰 Economics Analyst** - Market trends, pricing, economic impacts
4. **🌡️ Climate Researcher** - Weather patterns, climate adaptation
5. **🔬 Technology Advisor** - Modern farming tech, precision agriculture
6. **📋 Policy Analyst** - Agricultural policies, regulations, programs

## 📊 Answer Modes

### Detailed Analysis Mode (Default)
- Comprehensive multi-perspective analysis
- 500-1000+ words with full explanations
- Educational and research-focused
- Perfect for in-depth understanding

### Exact Answer Mode (`--exact` flag)
- Concise, practical, focused responses
- 200-300 words with direct recommendations
- Field-ready advice
- Mobile-friendly format

## 🔧 Configuration

### Ollama Setup
The system requires Ollama instances running on sequential ports:
- Primary: `localhost:11434`
- Secondary: `localhost:11435`
- Tertiary: `localhost:11436`

### Model Requirements
- Recommended: `gemma3:1b` (fast, lightweight)
- Alternative: `llama3:8b` (more capable, slower)
- Minimum: Any Ollama-compatible model

## 📚 Documentation

- [Complete Documentation](docs/README_AGRICULTURE_CHATBOT.md) - Full user guide and API reference
- [Implementation Summary](docs/AGRICULTURE_CHATBOT_SUMMARY.md) - Technical overview and achievements

## 🧪 Testing

```bash
# Run basic tests
python tests/test_agriculture_chatbot.py

# Run mode comparison demo
python tests/demo_agriculture_modes.py

# Interactive testing
python tests/test_agriculture_chatbot.py --interactive
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on the heavy-ollama multi-agent framework
- Uses Ollama for local LLM inference
- Integrates DuckDuckGo search for web content
- Designed specifically for agricultural knowledge applications

## 📞 Support

For issues, questions, or contributions:
- Create an issue in the repository
- Check the documentation in the `docs/` folder
- Review the test scripts for usage examples

---

**🌾 Made for farmers, by farmers - Empowering agriculture with AI** 🌾
