#!/bin/bash

# IndicAgri Bot Startup Script

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
RED='\033[0;31m'
NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Cleanup function for graceful shutdown
cleanup() {
    echo
    log_info "Shutting down IndicAgri Bot..."
    # Kill any background processes if needed
    exit 0
}

# Set up signal handlers for graceful shutdown
trap cleanup SIGINT SIGTERM

echo -e "${BLUE}Starting IndicAgri Bot...${NC}"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    log_error "Virtual environment not found at $VENV_PATH"
    log_error "Please run the installation script first: ./install_agri_bot.sh"
    exit 1
fi

# Activate virtual environment
log_info "Activating virtual environment..."
source "$VENV_PATH/bin/activate"

if [ $? -ne 0 ]; then
    log_error "Failed to activate virtual environment"
    exit 1
fi

log_success "Virtual environment activated"

# Check and install missing critical packages
check_and_install_packages() {
    log_info "Checking for missing critical packages..."
    
    missing_packages=()
    
    # Check for duckduckgo-search (critical for web search)
    if ! python3 -c "from duckduckgo_search import DDGS" >/dev/null 2>&1; then
        missing_packages+=("duckduckgo-search>=6.0.0")
    fi
    
    # Check for other critical packages
    if ! python3 -c "import flask" >/dev/null 2>&1; then
        missing_packages+=("flask>=3.0.0")
    fi
    
    if ! python3 -c "import flask_cors" >/dev/null 2>&1; then
        missing_packages+=("flask-cors>=6.0.0")
    fi
    
    if ! python3 -c "import duckduckgo_search" >/dev/null 2>&1; then
        missing_packages+=("duckduckgo-search>=8.0.0")
    fi
    
    if ! python3 -c "import requests" >/dev/null 2>&1; then
        missing_packages+=("requests>=2.28.0")
    fi
    
    if ! python3 -c "import bs4" >/dev/null 2>&1; then
        missing_packages+=("beautifulsoup4>=4.9.3")
    fi
    
    # Install missing packages if any
    if [ ${#missing_packages[@]} -gt 0 ]; then
        log_warning "Missing packages detected: ${missing_packages[*]}"
        log_info "Installing missing packages..."
        
        if pip install "${missing_packages[@]}"; then
            log_success "Missing packages installed successfully"
        else
            log_error "Failed to install some packages. Bot may not work correctly."
        fi
    else
        log_success "All critical packages are available"
    fi
}

# Run package check
check_and_install_packages

# Load environment variables
log_info "Loading environment variables..."
if [ -f "$PROJECT_ROOT/.env" ]; then
    source "$PROJECT_ROOT/.env"
    log_success "Environment variables loaded from .env"
else
    log_warning ".env file not found, using defaults"
fi

# Start ollama service if not running
log_info "Checking Ollama service..."
if ! pgrep -x "ollama" > /dev/null; then
    log_warning "Ollama service not running, attempting to start..."
    if command -v ollama >/dev/null 2>&1; then
        nohup ollama serve > /tmp/ollama.log 2>&1 &
        sleep 3
        if pgrep -x "ollama" > /dev/null; then
            log_success "Ollama service started"
        else
            log_warning "Failed to start Ollama service automatically"
        fi
    else
        log_warning "Ollama not installed - some features may not work"
    fi
else
    log_success "Ollama service is running"
fi

# Check if agri_bot_searcher directory exists
if [ ! -d "$AGRI_BOT_PATH" ]; then
    log_error "agri_bot_searcher directory not found at $AGRI_BOT_PATH"
    exit 1
fi

# Navigate to agri_bot_searcher directory
log_info "Navigating to agri_bot_searcher directory..."
cd "$AGRI_BOT_PATH"

# Check if enhanced RAG system is available
ENHANCED_AVAILABLE=false
RAG_PACKAGES_INSTALLED=false

log_info "Checking system capabilities..."

# Check if RAG dependencies are installed
if command -v python3 >/dev/null 2>&1; then
    if python3 -c "import sentence_transformers, faiss; print('RAG packages available')" >/dev/null 2>&1; then
        RAG_PACKAGES_INSTALLED=true
        log_success "RAG packages (sentence-transformers, FAISS) are installed"
    else
        log_warning "RAG packages not installed - lightweight mode only"
    fi
fi

# Check if embeddings database and RAG system exist
if [ -d "$EMBEDDINGS_PATH" ] && [ -f "$AGRI_BOT_PATH/src/enhanced_rag_system.py" ] && [ "$RAG_PACKAGES_INSTALLED" = "true" ]; then
    ENHANCED_AVAILABLE=true
    log_success "Enhanced RAG system is fully available"
else
    if [ ! -d "$EMBEDDINGS_PATH" ]; then
        log_warning "Embeddings database not found at $EMBEDDINGS_PATH"
    fi
    if [ ! -f "$AGRI_BOT_PATH/src/enhanced_rag_system.py" ]; then
        log_warning "Enhanced RAG system file not found"
    fi
fi

# Display startup information
echo
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    IndicAgri Bot Status                      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"

if [ "$RAG_PACKAGES_INSTALLED" = "true" ]; then
    echo -e "${GREEN}✓ RAG packages: sentence-transformers, FAISS available${NC}"
else
    echo -e "${YELLOW}✗ RAG packages: Not installed - lightweight mode only${NC}"
fi

if [ -d "$EMBEDDINGS_PATH" ]; then
    echo -e "${GREEN}✓ Embeddings database: Found at $EMBEDDINGS_PATH${NC}"
else
    echo -e "${YELLOW}✗ Embeddings database: Not found - web search only${NC}"
fi

if command -v ollama >/dev/null 2>&1 && pgrep -x "ollama" > /dev/null; then
    echo -e "${GREEN}✓ Ollama service: Running${NC}"
else
    echo -e "${YELLOW}✗ Ollama service: Not available${NC}"
fi

echo

# Start appropriate mode based on available components
log_info "Determining startup mode..."

# Start appropriate mode based on available components
log_info "Determining startup mode..."

if [ "$VOICE_ENABLED" = "true" ] && [ -f "src/enhanced_voice_web_ui.py" ]; then
    echo
    echo -e "${GREEN}🎤 Starting IndicAgri Bot with Voice Support${NC}"
    echo -e "${BLUE}Access the bot at: http://localhost:5000${NC}"
    echo -e "${YELLOW}Press CTRL+C to stop the server${NC}"
    echo
    python3 src/enhanced_voice_web_ui.py
elif [ "$ENHANCED_AVAILABLE" = "true" ] && [ -f "src/enhanced_web_ui.py" ]; then
    echo
    echo -e "${GREEN}🚀 Starting Enhanced IndicAgri Bot with RAG + Web Search${NC}"
    echo -e "${YELLOW}Features: Database retrieval, Web search, Sub-query generation, LLM synthesis${NC}"
    echo -e "${BLUE}Access the bot at: http://localhost:5000${NC}"
    echo -e "${YELLOW}Press CTRL+C to stop the server${NC}"
    echo
    python3 src/enhanced_web_ui.py
elif [ -f "src/web_ui.py" ]; then
    echo
    echo -e "${GREEN}⚡ Starting IndicAgri Bot (Lightweight Mode)${NC}"
    if [ "$RAG_PACKAGES_INSTALLED" = "false" ]; then
        echo -e "${YELLOW}Note: RAG packages not installed. Using web search only.${NC}"
    else
        echo -e "${YELLOW}Note: Embeddings database not found. Using web search only.${NC}"
    fi
    echo -e "${BLUE}Access the bot at: http://localhost:5000${NC}"
    echo -e "${YELLOW}Press CTRL+C to stop the server${NC}"
    echo
    python3 src/web_ui.py
else
    log_error "No valid web UI found!"
    log_error "Expected files: src/web_ui.py, src/enhanced_web_ui.py, or src/enhanced_voice_web_ui.py"
    log_error "Please check your installation."
    exit 1
fi
