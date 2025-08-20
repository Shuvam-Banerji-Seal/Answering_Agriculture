<<<<<<< HEAD

#!/bin/bash

# Agriculture Bot Searcher Startup Script
=======
#!/bin/bash

# IndicAgri Bot Startup Script
>>>>>>> 34a68fb (fixed .sh fails)

# Get the directory where this script is located (works regardless of where it's run from)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_PATH="$PROJECT_ROOT/agri_bot_env"
AGRI_BOT_PATH="$PROJECT_ROOT/agri_bot_searcher"
EMBEDDINGS_PATH="$PROJECT_ROOT/agriculture_embeddings"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

<<<<<<< HEAD
echo -e "\033[0;34mStarting Agriculture Bot Searcher...\033[0m"

# Activate virtual environment
source "/store/Answering_Agriculture/agri_bot_env/bin/activate"

# Load environment variables
if [ -f "/store/Answering_Agriculture/.env" ]; then
    source "/store/Answering_Agriculture/.env"
=======
echo -e "\033[0;34mStarting IndicAgri Bot...\033[0m"

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    source "$PROJECT_ROOT/.env"
>>>>>>> 34a68fb (fixed .sh fails)
fi

# Start ollama service if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama service..."
    ollama serve &
    sleep 3
fi

# Navigate to agri_bot_searcher directory
<<<<<<< HEAD
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
    python3 src/web_ui.py
fi


=======
cd "$AGRI_BOT_PATH"

# Check if enhanced RAG system is available
ENHANCED_AVAILABLE=false
RAG_PACKAGES_INSTALLED=false

# Check if RAG dependencies are installed
if command -v python3 >/dev/null 2>&1; then
    if python3 -c "import sentence_transformers, faiss; print('RAG packages available')" >/dev/null 2>&1; then
        RAG_PACKAGES_INSTALLED=true
    fi
fi

# Check if embeddings database and RAG system exist
if [ -d "$EMBEDDINGS_PATH" ] && [ -f "$AGRI_BOT_PATH/src/enhanced_rag_system.py" ] && [ "$RAG_PACKAGES_INSTALLED" = "true" ]; then
    ENHANCED_AVAILABLE=true
fi

# Display startup information
if [ "$RAG_PACKAGES_INSTALLED" = "true" ]; then
    echo -e "${BLUE}RAG packages installed: sentence-transformers, FAISS${NC}"
else
    echo -e "${YELLOW}RAG packages not installed - lightweight mode only${NC}"
fi

if [ -d "$EMBEDDINGS_PATH" ]; then
    echo -e "${BLUE}Embeddings database found: $EMBEDDINGS_PATH${NC}"
else
    echo -e "${YELLOW}Embeddings database not found - web search only${NC}"
fi

# Start appropriate mode
if [ "$VOICE_ENABLED" = "true" ]; then
    echo -e "${GREEN}Starting IndicAgri Bot with Voice Support${NC}"
    python3 src/enhanced_voice_web_ui.py
elif [ "$ENHANCED_AVAILABLE" = "true" ]; then
    echo -e "${GREEN}Starting Enhanced IndicAgri Bot with RAG + Web Search${NC}"
    echo -e "${YELLOW}Features: Database retrieval, Web search, Sub-query generation, LLM synthesis${NC}"
    python3 src/enhanced_web_ui.py
else
    echo -e "${GREEN}Starting IndicAgri Bot (Lightweight Mode)${NC}"
    if [ "$RAG_PACKAGES_INSTALLED" = "false" ]; then
        echo -e "${YELLOW}Note: RAG packages not installed. Using web search only.${NC}"
    else
        echo -e "${YELLOW}Note: Embeddings database not found. Using web search only.${NC}"
    fi
    python3 src/web_ui.py
fi
>>>>>>> 34a68fb (fixed .sh fails)
