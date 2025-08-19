#!/bin/bash

# Agriculture Bot Searcher Startup Script

# Get the directory where this script is located (works regardless of where it's run from)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_PATH="$PROJECT_ROOT/agri_bot_env"
AGRI_BOT_PATH="$PROJECT_ROOT/agri_bot_searcher"
<<<<<<< HEAD
EMBEDDINGS_PATH="$PROJECT_ROOT/agriculture_embeddings"
=======
>>>>>>> 4c50ca585c1b036becba0d3b754e883c5426d926

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
<<<<<<< HEAD
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "\033[0;34mStarting Agriculture Bot Searcher...\033[0m"

# Activate virtual environment
source "/store/Answering_Agriculture/agri_bot_env/bin/activate"

# Load environment variables
if [ -f "/store/Answering_Agriculture/.env" ]; then
    source "/store/Answering_Agriculture/.env"
=======
NC='\033[0m'

echo -e "${BLUE}Starting Agriculture Bot Searcher...${NC}"

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    source "$PROJECT_ROOT/.env"
>>>>>>> 4c50ca585c1b036becba0d3b754e883c5426d926
fi

# Start ollama service if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama service..."
<<<<<<< HEAD
    ollama serve &
    sleep 3
fi

# Navigate to agri_bot_searcher directory
cd "/store/Answering_Agriculture/agri_bot_searcher"

# Check if enhanced RAG system is available
ENHANCED_AVAILABLE=false
if [ -d "$EMBEDDINGS_PATH" ] && [ -f "$AGRI_BOT_PATH/src/enhanced_rag_system.py" ]; then
    ENHANCED_AVAILABLE=true
fi

# Check if voice is enabled
if [ "false" = "true" ]; then
    echo -e "${GREEN}Starting Agriculture Bot with Voice Support${NC}"
    python3 src/voice_web_ui.py
elif [ "$ENHANCED_AVAILABLE" = "true" ]; then
    echo -e "${GREEN}Starting Enhanced Agriculture Bot with RAG + Web Search${NC}"
    echo -e "${YELLOW}Features: Database retrieval, Web search, Sub-query generation, LLM synthesis${NC}"
    python3 src/enhanced_web_ui.py
else
    echo -e "${GREEN}Starting Agriculture Bot (Legacy Text Mode)${NC}"
    echo -e "${YELLOW}Note: Enhanced RAG mode not available. Missing embeddings database.${NC}"
=======
    nohup ollama serve > /tmp/ollama.log 2>&1 &
    sleep 5
    
    # Wait for ollama to be ready
    echo "Waiting for Ollama to be ready..."
    max_attempts=10
    attempt=1
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
            echo "✅ Ollama service is ready"
            break
        else
            echo "⏳ Waiting for Ollama... (attempt $attempt/$max_attempts)"
            sleep 2
            ((attempt++))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        echo "❌ Ollama failed to start. Please check the installation."
        exit 1
    fi
fi

# Check if gemma3:1b model is available
if ! ollama list 2>/dev/null | grep -q "gemma3:1b"; then
    echo "⬇️  gemma3:1b model not found. Downloading..."
    ollama pull gemma3:1b
    if [ $? -ne 0 ]; then
        echo "❌ Failed to download gemma3:1b model"
        echo "💡 Please run: ollama pull gemma3:1b"
        exit 1
    fi
fi

# Navigate to agri_bot_searcher directory
cd "$AGRI_BOT_PATH"

# Check if voice is enabled
if [ "$VOICE_ENABLED" = "true" ]; then
    echo -e "${GREEN}Starting Agriculture Bot with Voice Support${NC}"
    python3 src/voice_web_ui.py
else
    echo -e "${GREEN}Starting Agriculture Bot (Text Only)${NC}"
>>>>>>> 4c50ca585c1b036becba0d3b754e883c5426d926
    python3 src/web_ui.py
fi
