#!/bin/bash

# Agriculture Bot Searcher Startup Script

# Get the directory where this script is located (works regardless of where it's run from)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_PATH="$PROJECT_ROOT/agri_bot_env"
AGRI_BOT_PATH="$PROJECT_ROOT/agri_bot_searcher"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting Agriculture Bot Searcher...${NC}"

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    source "$PROJECT_ROOT/.env"
fi

# Start ollama service if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama service..."
    ollama serve &
    sleep 3
fi

# Navigate to agri_bot_searcher directory
cd "$AGRI_BOT_PATH"

# Check if voice is enabled
if [ "$VOICE_ENABLED" = "true" ]; then
    echo -e "${GREEN}Starting Agriculture Bot with Voice Support${NC}"
    python3 src/voice_web_ui.py
else
    echo -e "${GREEN}Starting Agriculture Bot (Text Only)${NC}"
    python3 src/web_ui.py
fi
