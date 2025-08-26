#!/bin/bash

# IndicAgri Bot Startup Script

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_PATH="$PROJECT_ROOT/agri_bot_env"
AGRI_BOT_PATH="$PROJECT_ROOT/agri_bot_searcher"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Starting IndicAgri Bot...${NC}"

# Check virtual environment
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}Virtual environment not found. Please run installation first.${NC}"
    exit 1
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    source "$PROJECT_ROOT/.env"
fi

# Start Ollama if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo -e "${YELLOW}Starting Ollama service...${NC}"
    if command -v systemctl &> /dev/null; then
        sudo systemctl start ollama
    else
        nohup ollama serve > /tmp/ollama.log 2>&1 &
        sleep 3
    fi
fi

# Navigate to application directory
cd "$AGRI_BOT_PATH"

# Check available UI modes
if [ "$VOICE_ENABLED" = "true" ] && [ -f "src/enhanced_voice_web_ui.py" ]; then
    echo -e "${GREEN}🎤 Starting IndicAgri Bot with Voice Support${NC}"
    echo -e "${BLUE}Access the bot at: http://localhost:5000${NC}"
    python3 src/enhanced_voice_web_ui.py --debug
elif [ "$RAG_ENABLED" = "true" ] && [ -f "src/enhanced_web_ui.py" ]; then
    echo -e "${GREEN}🚀 Starting IndicAgri Bot with RAG System${NC}"
    echo -e "${BLUE}Access the bot at: http://localhost:5000${NC}"
    python3 src/enhanced_web_ui.py --debug
else
    echo -e "${GREEN}⚡ Starting IndicAgri Bot (Basic Mode)${NC}"
    echo -e "${BLUE}Access the bot at: http://localhost:5000${NC}"
    python3 src/web_ui.py --debug
fi
