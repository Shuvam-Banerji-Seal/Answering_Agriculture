#!/bin/bash

# Agriculture Bot Searcher - Complete Installation Script
# This script installs all dependencies and sets up the environment for both text and voice input

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
# Get the directory where this script is located (works regardless of where it's run from)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_NAME="agri_bot_env"
VENV_PATH="$PROJECT_ROOT/$VENV_NAME"
AGRI_BOT_PATH="$PROJECT_ROOT/agri_bot_searcher"
VOICE_ENABLED=true

# System requirements check
check_system_requirements() {
    log_info "Checking system requirements..."
    
    # Check if running on Linux
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        log_warning "This script is optimized for Linux. Some features may not work on other systems."
    fi
    
    # Check Python 3.8+
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    log_info "Found Python $python_version"
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 is required but not installed."
        exit 1
    fi
    
    # Check git
    if ! command -v git &> /dev/null; then
        log_error "git is required but not installed."
        exit 1
    fi
    
    # Check curl for ollama installation
    if ! command -v curl &> /dev/null; then
        log_error "curl is required but not installed."
        exit 1
    fi
    
    log_success "System requirements check passed"
}

# Create and setup virtual environment
setup_virtual_environment() {
    log_info "Setting up Python virtual environment..."
    
    cd "$PROJECT_ROOT"
    
    # Remove existing virtual environment if it exists
    if [ -d "$VENV_PATH" ]; then
        log_warning "Existing virtual environment found. Removing..."
        rm -rf "$VENV_PATH"
    fi
    
    # Create new virtual environment
    python3 -m venv "$VENV_NAME"
    source "$VENV_PATH/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    log_success "Virtual environment created and activated"
}

# Install base Python dependencies
install_base_dependencies() {
    log_info "Installing base Python dependencies..."
    
    source "$VENV_PATH/bin/activate"
    
    # Install core agri_bot_searcher dependencies
    if [ -f "$AGRI_BOT_PATH/requirements.txt" ]; then
        pip install -r "$AGRI_BOT_PATH/requirements.txt"
        log_success "Base dependencies installed"
    else
        log_warning "requirements.txt not found, installing core packages manually"
        pip install requests duckduckgo-search flask flask-cors pyyaml beautifulsoup4 lxml urllib3 html5lib dataclasses-json colorlog
    fi
}

# Install Ollama
install_ollama() {
    log_info "Installing Ollama..."
    
    # Check if ollama is already installed
    if command -v ollama &> /dev/null; then
        log_warning "Ollama is already installed"
        ollama --version
    else
        # Install ollama
        curl -fsSL https://ollama.ai/install.sh | sh
        log_success "Ollama installed"
    fi
    
    # Start ollama service
    log_info "Starting Ollama service..."
    if pgrep -x "ollama" > /dev/null; then
        log_warning "Ollama service is already running"
    else
        ollama serve &
        sleep 5  # Wait for service to start
        log_success "Ollama service started"
    fi
    
    # Pull gemma3:1b model
    log_info "Downloading gemma3:1b model..."
    if ollama list | grep -q "gemma3:1b"; then
        log_warning "gemma3:1b model already exists"
    else
        ollama pull gemma3:1b
        log_success "gemma3:1b model downloaded"
    fi
}

# Install voice dependencies (NeMo, IndicTrans, etc.)
install_voice_dependencies() {
    log_info "Installing voice transcription dependencies..."
    
    source "$VENV_PATH/bin/activate"
    
    # Check if voice requirements file exists
    if [ -f "$AGRI_BOT_PATH/requirements_voice.txt" ]; then
        log_info "Installing voice dependencies from requirements_voice.txt..."
        pip install -r "$AGRI_BOT_PATH/requirements_voice.txt"
    else
        log_info "Installing voice dependencies manually..."
        
        # Core audio processing
        pip install torch torchaudio
        
        # NeMo toolkit
        pip install nemo-toolkit[asr]
        
        # IndicTrans dependencies
        pip install transformers sentencepiece sacremoses
        
        # SarvamAI (if available)
        pip install sarvam-ai || log_warning "SarvamAI not available, skipping..."
        
        # Additional audio processing
        pip install librosa soundfile pyaudio || log_warning "Some audio packages failed, continuing..."
    fi
    
    log_success "Voice dependencies installation completed"
}

# Test voice functionality
test_voice_functionality() {
    log_info "Testing voice functionality..."
    
    source "$VENV_PATH/bin/activate"
    cd "$AGRI_BOT_PATH"
    
    # Test if we can import voice transcription modules
    python3 -c "
import sys
sys.path.append('src')
try:
    from voice_transcription import VoiceTranscription
    print('✓ Voice transcription module imported successfully')
except ImportError as e:
    print(f'✗ Voice transcription import failed: {e}')
    sys.exit(1)
" && VOICE_ENABLED=true || {
        log_warning "Voice functionality test failed. Continuing with text-only mode."
        VOICE_ENABLED=false
    }
}

# Setup environment file
setup_environment() {
    log_info "Setting up environment configuration..."
    
    cd "$PROJECT_ROOT"
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        cp "$AGRI_BOT_PATH/.env.example" ".env" 2>/dev/null || {
            cat > ".env" << EOF
# Agriculture Bot Environment Configuration

# Hugging Face Token (optional, for advanced models)
# HUGGINGFACE_TOKEN=your_token_here

# SarvamAI API Key (optional, for voice transcription)
# SARVAM_API_KEY=your_api_key_here

# Voice transcription settings
VOICE_ENABLED=$VOICE_ENABLED
DEFAULT_VOICE_ENGINE=conformer

# Ollama settings
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma3:1b

# Web UI settings
WEB_HOST=0.0.0.0
WEB_PORT=5000
EOF
        }
        log_success "Environment file created"
    else
        log_warning "Environment file already exists, skipping creation"
    fi
}

# Create startup script
create_startup_script() {
    log_info "Creating startup script..."
    
    cat > "$PROJECT_ROOT/start_agri_bot.sh" << EOF
#!/bin/bash

# Agriculture Bot Searcher Startup Script

# Get the directory where this script is located (works regardless of where it's run from)
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="\$SCRIPT_DIR"
VENV_PATH="\$PROJECT_ROOT/agri_bot_env"
AGRI_BOT_PATH="\$PROJECT_ROOT/agri_bot_searcher"

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
EOF

    chmod +x "$PROJECT_ROOT/start_agri_bot.sh"
    log_success "Startup script created"
}

# Test basic functionality
test_basic_functionality() {
    log_info "Testing basic functionality..."
    
    source "$VENV_PATH/bin/activate"
    cd "$AGRI_BOT_PATH"
    
    # Test agriculture chatbot import
    python3 -c "
import sys
sys.path.append('src')
try:
    from agriculture_chatbot import AgricultureChatbot
    print('✓ Agriculture chatbot imported successfully')
except ImportError as e:
    print(f'✗ Agriculture chatbot import failed: {e}')
    sys.exit(1)
" || {
        log_error "Basic functionality test failed"
        return 1
    }
    
    # Test ollama connection
    if command -v ollama &> /dev/null; then
        if ollama list | grep -q "gemma3:1b"; then
            log_success "Ollama and gemma3:1b model are ready"
        else
            log_warning "gemma3:1b model not found in ollama"
        fi
    else
        log_warning "Ollama not found"
    fi
}

# Main installation function
main() {
    echo -e "${BLUE}Agriculture Bot Searcher - Complete Installation${NC}"
    echo "=============================================="
    
    check_system_requirements
    setup_virtual_environment
    install_base_dependencies
    
    # Install ollama (with error handling)
    if install_ollama; then
        log_success "Ollama installation completed"
    else
        log_warning "Ollama installation failed, continuing without it"
    fi
    
    # Install voice dependencies (with error handling)
    if install_voice_dependencies; then
        test_voice_functionality
    else
        log_warning "Voice dependencies installation failed, continuing with text-only mode"
        VOICE_ENABLED=false
    fi
    
    setup_environment
    create_startup_script
    
    # Test functionality
    if test_basic_functionality; then
        log_success "Installation completed successfully!"
    else
        log_warning "Installation completed with some issues"
    fi
    
    echo
    echo -e "${GREEN}Installation Summary:${NC}"
    echo "===================="
    echo -e "Virtual Environment: ${VENV_PATH}"
    echo -e "Voice Support: $([ "$VOICE_ENABLED" = "true" ] && echo "✓ Enabled" || echo "✗ Disabled")"
    echo -e "Ollama Model: $(command -v ollama &> /dev/null && ollama list | grep -q "gemma3:1b" && echo "✓ gemma3:1b ready" || echo "✗ Not available")"
    echo
    echo -e "${BLUE}To start the application:${NC}"
    echo "cd $PROJECT_ROOT"
    echo "./start_agri_bot.sh"
    echo
    echo -e "${BLUE}Or manually:${NC}"
    echo "source $VENV_PATH/bin/activate"
    echo "cd $AGRI_BOT_PATH"
    if [ "$VOICE_ENABLED" = "true" ]; then
        echo "python3 src/voice_web_ui.py"
    else
        echo "python3 src/web_ui.py"
    fi
}

# Handle script termination
cleanup() {
    log_info "Cleaning up..."
    # Kill ollama serve if we started it
    if pgrep -f "ollama serve" > /dev/null; then
        pkill -f "ollama serve" 2>/dev/null || true
    fi
}

trap cleanup EXIT

# Run main installation
main "$@"
