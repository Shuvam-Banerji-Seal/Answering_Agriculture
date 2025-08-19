# Agriculture Multi-Agent Chatbot 🌾

A sophisticated chatbot system that deploys multiple specialized Ollama agents to search the internet and provide comprehensive answers to agricultural queries with inline citations.

## Features

- **Multi-Agent System**: Deploys specialized agents with different agricultural expertise
- **Web Search Integration**: Real-time internet search for current information
- **Inline Citations**: Automatic citation generation with source links
- **Agriculture Focus**: Enhanced search queries and domain-specific optimization
- **Parallel Processing**: Concurrent agent execution for faster responses
- **Robust Error Handling**: Graceful handling of agent failures and timeouts
- **Exact Answer Mode**: Concise, focused responses vs. detailed analysis

## Agent Specializations

The system includes the following specialized agents:

1. **Crop Specialist** - Crop varieties, cultivation practices, yield optimization
2. **Disease Expert** - Plant pathology, pest management, diagnosis, treatment
3. **Economics Analyst** - Market trends, pricing, economic impacts
4. **Climate Researcher** - Climate impacts, weather patterns, adaptation
5. **Technology Advisor** - Modern farming tech, precision agriculture
6. **Policy Analyst** - Agricultural policies, regulations, government programs

## Prerequisites

1. **Ollama Installation**
   - Install Ollama from: https://ollama.ai/download
   - Verify installation: `ollama --version`

2. **Python Requirements**
   - Python 3.7+
   - Install dependencies: `pip install -r requirements_chatbot.txt`

## Quick Start

### 1. Setup

Run the setup script to install dependencies and get configuration instructions:

```bash
python setup_agriculture_chatbot.py
```

### 2. Start Ollama Instances

Open 3 separate terminal windows and run:

**Terminal 1:**
```bash
export OLLAMA_HOST=0.0.0.0:11434
ollama serve
```

**Terminal 2:**
```bash
export OLLAMA_HOST=0.0.0.0:11435
ollama serve
```

**Terminal 3:**
```bash
export OLLAMA_HOST=0.0.0.0:11436
ollama serve
```

### 3. Download Model

In another terminal:
```bash
ollama pull gemma2:2b
```

### 4. Test the Chatbot

Run the test script:
```bash
python test_agriculture_chatbot.py
```

Or use interactive mode:
```bash
python test_agriculture_chatbot.py --interactive
```

## Usage

### Command Line Interface

```bash
python agriculture_chatbot.py --query "How to treat bacterial blight in rice?" --agents 3 --searches 2
```

Parameters:
- `--query, -q`: Agricultural query to answer (required)
- `--agents, -a`: Number of agents to deploy (default: 3)
- `--searches, -s`: Number of searches per agent (default: 2)
- `--port, -p`: Base Ollama port (default: 11434)
- `--exact, -e`: Generate concise, exact answer instead of detailed analysis

#### Answer Modes

**Detailed Mode (default)**: Provides comprehensive analysis from multiple agent perspectives
```bash
python agriculture_chatbot.py --query "Best rice cultivation practices?" --agents 2
```

**Exact Answer Mode**: Provides concise, practical, focused answers
```bash
python agriculture_chatbot.py --query "Best rice cultivation practices?" --agents 2 --exact
```

### Python API

```python
from agriculture_chatbot import AgricultureChatbot

# Create chatbot instance
chatbot = AgricultureChatbot(base_port=11434, num_agents=3)

# Detailed analysis mode
result = chatbot.answer_query(
    query="What are the best practices for organic farming?",
    num_searches=2,
    exact_answer=False
)

# Exact answer mode
result_exact = chatbot.answer_query(
    query="What are the best practices for organic farming?",
    num_searches=2,
    exact_answer=True
)

if result["success"]:
    print("Detailed Analysis:")
    print(result["answer"])
    print(f"Citations: {len(result['citations'])}")
    
if result_exact["success"]:
    print("
Exact Answer:")
    print(result_exact["answer"])
```

## Example Queries

- "What are the best practices for rice cultivation in monsoon season?"
- "How to identify and treat bacterial blight in rice plants?"
- "What are the current market prices for wheat in India?"
- "How does climate change affect crop yields?"
- "What are the latest precision farming technologies?"
- "What government subsidies are available for organic farming?"
- "How to implement integrated pest management in cotton crops?"
- "What are the soil requirements for growing quinoa?"

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                Agriculture Chatbot Orchestrator             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Agent 1   │  │   Agent 2   │  │   Agent 3   │          │
│  │ Crop Spec.  │  │ Disease Exp.│  │ Econ. Anal. │   ...    │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│               Web Search Engine (DuckDuckGo)                │
├─────────────────────────────────────────────────────────────┤
│    ┌───────────┐    ┌───────────┐    ┌───────────┐          │
│    │ Ollama    │    │ Ollama    │    │ Ollama    │          │
│    │ :11434    │    │ :11435    │    │ :11436    │   ...    │
│    └───────────┘    └───────────┘    └───────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### Workflow

1. **Query Processing**: Enhanced query generation for agricultural domains
2. **Agent Deployment**: Parallel deployment of specialized agents
3. **Web Search**: Each agent performs multiple targeted web searches
4. **Content Analysis**: Agents analyze search results using Ollama LLMs
5. **Response Synthesis**: Combine agent responses with inline citations
6. **Result Formatting**: Structure final answer with sources and metadata

## Configuration

### Custom Agent Roles

You can extend the system by adding new agent roles in `agriculture_chatbot.py`:

```python
class AgentRole(Enum):
    # Add new roles here
    LIVESTOCK_EXPERT = "livestock_expert"
    SOIL_SCIENTIST = "soil_scientist"
```

### Search Configuration

Modify search behavior in the `AgricultureSearchEngine` class:

```python
# Customize agriculture-specific domains
self.agriculture_domains = [
    'extension.org', 'agric.gov', 'fao.org', 'usda.gov',
    # Add more trusted agricultural sources
]
```

### Model Configuration

Change the default model by modifying:

```python
AgricultureAgent(agent_id, role, port, model="gemma2:2b")
```

Available models:
- `gemma2:2b` (fast, lightweight)
- `llama3:8b` (more capable, slower)
- `mistral:7b` (balanced performance)

## Troubleshooting

### Common Issues

1. **No Ollama instances available**
   - Ensure Ollama is installed and running
   - Check that ports 11434-11436 are not in use
   - Verify model is downloaded: `ollama list`

2. **Slow responses**
   - Use a smaller model (e.g., `gemma2:2b`)
   - Reduce number of searches per agent
   - Reduce number of agents

3. **Search failures**
   - Check internet connectivity
   - Verify DuckDuckGo is accessible
   - Check for rate limiting

4. **Agent failures**
   - Check Ollama logs for errors
   - Verify sufficient system resources
   - Try restarting Ollama instances

### Performance Tuning

- **Faster responses**: Use `gemma2:2b` model, reduce agents to 2, limit searches to 1
- **Better quality**: Use `llama3:8b` model, increase agents to 5, increase searches to 3
- **Balanced**: Default settings with `gemma2:2b`, 3 agents, 2 searches

## File Structure

```
agriculture_chatbot.py          # Main chatbot implementation
test_agriculture_chatbot.py     # Test script and interactive mode
setup_agriculture_chatbot.py    # Setup and configuration helper
requirements_chatbot.txt        # Python dependencies
README_AGRICULTURE_CHATBOT.md   # This documentation
```

## Contributing

To extend the system:

1. Add new agent roles in the `AgentRole` enum
2. Customize system prompts for new roles
3. Enhance search query generation for specific domains
4. Add new agricultural domain sources
5. Improve citation formatting and source validation

## License

This project is based on the heavy-ollama framework and is provided for educational and research purposes.

## Acknowledgments

- Built on the heavy-ollama multi-agent framework
- Uses Ollama for local LLM inference
- Integrates DuckDuckGo search for web content
- Designed specifically for agricultural knowledge applications
