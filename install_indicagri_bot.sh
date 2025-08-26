#!/bin/bash

# IndicAgri Bot - Streamlined Installation Script
# Unified installation for agriculture chatbot with voice capabilities

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_NAME="agri_bot_env"
VENV_PATH="$PROJECT_ROOT/$VENV_NAME"
AGRI_BOT_PATH="$PROJECT_ROOT/agri_bot_searcher"
REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"

# Installation options
VOICE_ENABLED=true
RAG_ENABLED=true
OLLAMA_MODEL="llama3.2:3b"

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-voice)
                VOICE_ENABLED=false
                shift
                ;;
            --no-rag)
                RAG_ENABLED=false
                shift
                ;;
            --model)
                OLLAMA_MODEL="$2"
                shift 2
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_warning "Unknown option: $1"
                shift
                ;;
        esac
    done
}

# Show help information
show_help() {
    echo "IndicAgri Bot Installation Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --no-voice     Disable voice transcription features"
    echo "  --no-rag       Disable RAG (Retrieval Augmented Generation) system"
    echo "  --model MODEL  Set Ollama model (default: llama3.2:3b)"
    echo "  --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Full installation with all features"
    echo "  $0 --no-voice        # Install without voice features"
    echo "  $0 --model gemma2:2b # Use Gemma model instead of Llama"
}

# System requirements check
check_system_requirements() {
    log_info "Checking system requirements..."
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    python3 -c "
import sys
if sys.version_info < (3, 8):
    print(f'Python 3.8 or higher is required (found: {sys.version_info.major}.{sys.version_info.minor})')
    exit(1)
else:
    print(f'Python version {sys.version_info.major}.{sys.version_info.minor} is compatible')
    exit(0)
"
    if [ $? -ne 0 ]; then
        log_error "Python version check failed"
        exit 1
    fi
    
    # Check for pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 is required but not installed"
        exit 1
    fi
    
    # Check for git
    if ! command -v git &> /dev/null; then
        log_error "git is required but not installed"
        exit 1
    fi
    
    log_success "System requirements check passed"
}

# Create and setup virtual environment
setup_virtual_environment() {
    log_info "Setting up virtual environment..."
    
    if [ -d "$VENV_PATH" ]; then
        log_warning "Virtual environment already exists. Removing..."
        rm -rf "$VENV_PATH"
    fi
    
    python3 -m venv "$VENV_PATH"
    source "$VENV_PATH/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    log_success "Virtual environment created and activated"
}

# Install Python dependencies
install_python_dependencies() {
    log_info "Installing Python dependencies from unified requirements.txt..."
    
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        log_error "Requirements file not found: $REQUIREMENTS_FILE"
        exit 1
    fi
    
    # Install core dependencies
    pip install -r "$REQUIREMENTS_FILE"
    
    log_success "Python dependencies installed successfully"
}

# Install Ollama
install_ollama() {
    log_info "Installing Ollama..."
    
    if command -v ollama &> /dev/null; then
        log_success "Ollama already installed"
        return
    fi
    
    # Install Ollama
    curl -fsSL https://ollama.ai/install.sh | sh
    
    # Start Ollama service
    if command -v systemctl &> /dev/null; then
        sudo systemctl enable ollama
        sudo systemctl start ollama
    else
        # Start Ollama in background for non-systemd systems
        nohup ollama serve > /tmp/ollama.log 2>&1 &
    fi
    
    # Wait for Ollama to start
    sleep 5
    
    # Pull the specified model
    log_info "Downloading Ollama model: $OLLAMA_MODEL"
    ollama pull "$OLLAMA_MODEL"
    
    log_success "Ollama installed and model downloaded"
}

# Setup environment file
setup_environment() {
    log_info "Setting up environment configuration..."
    
    cat > "$PROJECT_ROOT/.env" << EOF
# IndicAgri Bot Environment Configuration
# Generated on $(date)

# Voice transcription settings
VOICE_ENABLED=$VOICE_ENABLED
DEFAULT_VOICE_ENGINE=conformer

# RAG system settings
RAG_ENABLED=$RAG_ENABLED
RAG_MODEL=Qwen/Qwen3-Embedding-8B

# Ollama settings
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=$OLLAMA_MODEL

# Web UI settings
WEB_HOST=0.0.0.0
WEB_PORT=5000

# API Keys (set these if using external services)
# HUGGINGFACE_TOKEN=your_token_here
# SARVAM_API_KEY=your_api_key_here

# Logging
LOG_LEVEL=INFO
EOF
    
    log_success "Environment file created at $PROJECT_ROOT/.env"
}

# Create startup script
create_startup_script() {
    log_info "Creating startup script..."
    
    cat > "$PROJECT_ROOT/start_indicagri_bot.sh" << 'EOF'
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
    python3 src/enhanced_voice_web_ui.py
elif [ "$RAG_ENABLED" = "true" ] && [ -f "src/enhanced_web_ui.py" ]; then
    echo -e "${GREEN}🚀 Starting IndicAgri Bot with RAG System${NC}"
    echo -e "${BLUE}Access the bot at: http://localhost:5000${NC}"
    python3 src/enhanced_web_ui.py
else
    echo -e "${GREEN}⚡ Starting IndicAgri Bot (Basic Mode)${NC}"
    echo -e "${BLUE}Access the bot at: http://localhost:5000${NC}"
    python3 src/web_ui.py
fi
EOF
    
    chmod +x "$PROJECT_ROOT/start_indicagri_bot.sh"
    
    log_success "Startup script created: start_indicagri_bot.sh"
}

# Main installation function
main() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                  IndicAgri Bot Installer                     ║${NC}"
    echo -e "${BLUE}║              Agriculture Chatbot with Voice AI              ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    parse_arguments "$@"
    
    log_info "Installation configuration:"
    log_info "  Voice Features: $VOICE_ENABLED"
    log_info "  RAG System: $RAG_ENABLED"
    log_info "  Ollama Model: $OLLAMA_MODEL"
    echo
    
    check_system_requirements
    setup_virtual_environment
    install_python_dependencies
    install_ollama
    setup_environment
    create_startup_script
    
    echo
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                   Installation Complete!                    ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${BLUE}To start IndicAgri Bot:${NC}"
    echo -e "${YELLOW}  ./start_indicagri_bot.sh${NC}"
    echo
    echo -e "${BLUE}Or manually:${NC}"
    echo -e "${YELLOW}  source agri_bot_env/bin/activate${NC}"
    echo -e "${YELLOW}  cd agri_bot_searcher${NC}"
    echo -e "${YELLOW}  python3 src/enhanced_voice_web_ui.py${NC}"
    echo
    echo -e "${BLUE}Access the web interface at: http://localhost:5000${NC}"
    echo
}

# Run main function
main "$@"
