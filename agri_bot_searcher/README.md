# Agriculture Bot Searcher 🌾

A sophisticated multi-agent chatbot system that deploys specialized Ollama agents to search the internet and provide comprehensive answers to agricultural queries with inline citations.

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- **🤖 Multi-Agent System**: Deploys specialized agents with different agricultural expertise
- **🔍 Real-time Web Search**: Internet search integration for current information
- **📚 Inline Citations**: Automatic citation generation with source links
- **🌱 Agriculture-Focused**: Enhanced queries and domain-specific optimization
- **⚡ Dual Answer Modes**: Choose between detailed analysis or concise practical advice
- **🛡️ Robust Error Handling**: Graceful handling of agent failures and timeouts

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- [Ollama](https://ollama.ai/download) installed and running
- Internet connection for web search

### Installation

1. **Clone or extract the project**:
   ```bash
   cd agri_bot_searcher
   ```

2. **Run the install script**:
   ```bash
   ./install.sh
   ```

   Or manually:
   ```bash
   pip install -r requirements.txt
   python scripts/setup_agriculture_chatbot.py
   ```

3. **Start Ollama instances** (follow the setup script instructions)

### Usage

#### Command Line
```bash
# Detailed analysis
python src/agriculture_chatbot.py --query "How to treat bacterial blight in rice?" --agents 2

# Concise answer
python src/agriculture_chatbot.py --query "Best fertilizer for wheat" --exact

# Interactive mode
python tests/test_agriculture_chatbot.py
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
