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
    python3 src/web_ui.py
fi
