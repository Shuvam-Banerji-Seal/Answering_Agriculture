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
    
    # Always install critical dependencies first
    log_info "Installing critical core packages..."
    pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
<<<<<<< HEAD
    pip install ddgs>=0.2.0 requests>=2.28.0
    pip install flask>=2.0.0 flask-cors>=4.0.0 pyyaml>=6.0
    pip install beautifulsoup4>=4.9.3 lxml>=4.6.3 urllib3>=1.26.0
    pip install html5lib>=1.1 dataclasses-json>=0.5.0 colorlog>=6.0.0
    pip install numpy>=1.21.0
    
    # Install Enhanced RAG dependencies with GPU detection
    log_info "Installing Enhanced RAG dependencies..."
    pip install sentence-transformers>=2.2.0
    
    # Smart FAISS installation - try GPU first, fallback to CPU
    log_info "Installing FAISS with GPU detection..."
    
    # Check if NVIDIA GPU is available
    if command -v nvidia-smi >/dev/null 2>&1; then
        log_info "NVIDIA GPU detected, attempting FAISS-GPU installation..."
        if pip install faiss-gpu>=1.7.0; then
            log_success "FAISS-GPU installed successfully"
        else
            log_warning "FAISS-GPU installation failed, falling back to CPU version"
            pip install faiss-cpu>=1.7.0
        fi
    else
        log_info "No GPU detected, installing FAISS-CPU"
        pip install faiss-cpu>=1.7.0
    fi
=======
    pip install duckduckgo-search>=6.0.0 requests>=2.28.0
    pip install flask>=2.0.0 flask-cors>=4.0.0 pyyaml>=6.0
    pip install beautifulsoup4>=4.9.3 lxml>=4.6.3 urllib3>=1.26.0
    pip install html5lib>=1.1 dataclasses-json>=0.5.0 colorlog>=6.0.0
>>>>>>> 4c50ca585c1b036becba0d3b754e883c5426d926
    
    # Install from requirements file if available
    if [ -f "$AGRI_BOT_PATH/requirements.txt" ]; then
        log_info "Installing additional dependencies from requirements.txt..."
        pip install -r "$AGRI_BOT_PATH/requirements.txt"
    fi
    
    # Install complete requirements if available
    if [ -f "$AGRI_BOT_PATH/requirements_complete.txt" ]; then
<<<<<<< HEAD
                        log_info "Installing complete dependencies..."
=======
        log_info "Installing complete dependencies..."
>>>>>>> 4c50ca585c1b036becba0d3b754e883c5426d926
        pip install -r "$AGRI_BOT_PATH/requirements_complete.txt" || {
            log_warning "Some packages from complete requirements failed, continuing..."
        }
    fi
    
<<<<<<< HEAD
    # Install RAG-specific dependencies
    log_info "Installing Enhanced RAG dependencies..."
    pip install sentence-transformers>=2.2.0 faiss-cpu>=1.7.0 || {
        log_warning "Some RAG dependencies failed to install"
    }
    
=======
>>>>>>> 4c50ca585c1b036becba0d3b754e883c5426d926
    log_success "Base dependencies installed"
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
        # Start ollama in background
        nohup ollama serve > /tmp/ollama.log 2>&1 &
        sleep 8  # Wait longer for service to start properly
        
        # Verify ollama is responding
        local max_attempts=10
        local attempt=1
        while [ $attempt -le $max_attempts ]; do
            if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
                log_success "Ollama service started and responding"
                break
            else
                log_info "Waiting for Ollama to start... (attempt $attempt/$max_attempts)"
                sleep 3
                ((attempt++))
            fi
        done
        
        if [ $attempt -gt $max_attempts ]; then
            log_error "Ollama service failed to start properly"
            return 1
        fi
    fi
    
    # Pull gemma3:1b model with error handling
    log_info "Downloading gemma3:1b model (this may take several minutes)..."
    if ollama list 2>/dev/null | grep -q "gemma3:1b"; then
        log_warning "gemma3:1b model already exists"
    else
        log_info "Downloading gemma3:1b model... This may take 5-10 minutes depending on your connection."
        if ollama pull gemma3:1b; then
            log_success "gemma3:1b model downloaded successfully"
        else
            log_error "Failed to download gemma3:1b model"
            log_warning "You can download it manually later with: ollama pull gemma3:1b"
            return 1
        fi
    fi
    
<<<<<<< HEAD
    # Pull gemma3:27b model for synthesis (optional but recommended)
    log_info "Downloading gemma3:27b model for answer synthesis (this may take 15-20 minutes)..."
    if ollama list 2>/dev/null | grep -q "gemma3:27b"; then
        log_warning "gemma3:27b model already exists"
    else
        log_info "Downloading gemma3:27b model... This is a large model and may take 15-20 minutes."
        if ollama pull gemma3:27b; then
            log_success "gemma3:27b model downloaded successfully"
        else
            log_warning "Failed to download gemma3:27b model. You can download it manually later with: ollama pull gemma3:27b"
            log_warning "The system will use gemma3:1b as fallback for synthesis"
        fi
    fi
    
    # Verify models are available
=======
    # Verify model is available
>>>>>>> 4c50ca585c1b036becba0d3b754e883c5426d926
    if ollama list 2>/dev/null | grep -q "gemma3:1b"; then
        log_success "gemma3:1b model is ready for use"
    else
        log_warning "gemma3:1b model verification failed"
    fi
<<<<<<< HEAD
    
    if ollama list 2>/dev/null | grep -q "gemma3:27b"; then
        log_success "gemma3:27b model is ready for use"
    else
        log_info "gemma3:27b model not available - gemma3:1b will be used for synthesis"
    fi
=======
>>>>>>> 4c50ca585c1b036becba0d3b754e883c5426d926
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
<<<<<<< HEAD
EMBEDDINGS_PATH="\$PROJECT_ROOT/agriculture_embeddings"
=======
>>>>>>> 4c50ca585c1b036becba0d3b754e883c5426d926

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
<<<<<<< HEAD
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "\033[0;34mStarting Agriculture Bot Searcher...\033[0m"
=======
NC='\033[0m'

echo -e "${BLUE}Starting Agriculture Bot Searcher...${NC}"
>>>>>>> 4c50ca585c1b036becba0d3b754e883c5426d926

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

<<<<<<< HEAD
# Check if enhanced RAG system is available
ENHANCED_AVAILABLE=false
if [ -d "\$EMBEDDINGS_PATH" ] && [ -f "\$AGRI_BOT_PATH/src/enhanced_rag_system.py" ]; then
    ENHANCED_AVAILABLE=true
fi

# Check if voice is enabled
if [ "$VOICE_ENABLED" = "true" ]; then
    echo -e "\${GREEN}Starting Agriculture Bot with Voice Support\${NC}"
    python3 src/voice_web_ui.py
elif [ "\$ENHANCED_AVAILABLE" = "true" ]; then
    echo -e "\${GREEN}Starting Enhanced Agriculture Bot with RAG + Web Search\${NC}"
    echo -e "\${YELLOW}Features: Database retrieval, Web search, Sub-query generation, LLM synthesis\${NC}"
    python3 src/enhanced_web_ui.py
else
    echo -e "\${GREEN}Starting Agriculture Bot (Legacy Text Mode)\${NC}"
    echo -e "\${YELLOW}Note: Enhanced RAG mode not available. Missing embeddings database.\${NC}"
=======
# Check if voice is enabled
if [ "$VOICE_ENABLED" = "true" ]; then
    echo -e "${GREEN}Starting Agriculture Bot with Voice Support${NC}"
    python3 src/voice_web_ui.py
else
    echo -e "${GREEN}Starting Agriculture Bot (Text Only)${NC}"
>>>>>>> 4c50ca585c1b036becba0d3b754e883c5426d926
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
    
    # Test critical imports
    log_info "Testing Python dependencies..."
    python3 -c "
import sys
sys.path.append('src')

# Test critical packages
try:
    import torch
    print('✓ PyTorch imported successfully')
except ImportError as e:
    print(f'✗ PyTorch import failed: {e}')
    sys.exit(1)

try:
    from duckduckgo_search import DDGS
    print('✓ DuckDuckGo Search imported successfully')
except ImportError as e:
    print(f'✗ DuckDuckGo Search import failed: {e}')
    sys.exit(1)

try:
    from agriculture_chatbot import AgricultureChatbot
    print('✓ Agriculture chatbot imported successfully')
except ImportError as e:
    print(f'✗ Agriculture chatbot import failed: {e}')
    sys.exit(1)
" || {
        log_error "Critical dependency test failed"
        return 1
    }
    
    # Test ollama connection and model
    if command -v ollama &> /dev/null; then
        log_info "Testing Ollama connectivity..."
        
        # Check if service is running
        if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
            log_success "Ollama service is responding"
            
            # Check if gemma3:1b model exists
            if ollama list 2>/dev/null | grep -q "gemma3:1b"; then
                log_success "gemma3:1b model is available"
                
                # Test model inference
                log_info "Testing model inference..."
                if echo "Hello" | ollama run gemma3:1b --format json > /dev/null 2>&1; then
                    log_success "gemma3:1b model is working correctly"
                else
                    log_warning "gemma3:1b model inference test failed"
                fi
<<<<<<< HEAD
                
                # Test gemma3:27b if available
                if ollama list 2>/dev/null | grep -q "gemma3:27b"; then
                    log_info "Testing gemma3:27b model inference..."
                    if echo "Test" | ollama run gemma3:27b --format json > /dev/null 2>&1; then
                        log_success "gemma3:27b model is working correctly"
                    else
                        log_warning "gemma3:27b model inference test failed"
                    fi
                fi
=======
>>>>>>> 4c50ca585c1b036becba0d3b754e883c5426d926
            else
                log_warning "gemma3:1b model not found - attempting to download..."
                if ollama pull gemma3:1b; then
                    log_success "gemma3:1b model downloaded successfully"
                else
                    log_error "Failed to download gemma3:1b model"
                    return 1
                fi
            fi
        else
            log_warning "Ollama service not responding - attempting to start..."
            nohup ollama serve > /tmp/ollama.log 2>&1 &
            sleep 5
            
            if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
                log_success "Ollama service started successfully"
            else
                log_error "Failed to start Ollama service"
                return 1
            fi
        fi
    else
        log_error "Ollama not found"
        return 1
    fi
    
    log_success "All basic functionality tests passed"
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
<<<<<<< HEAD
    echo -e "Ollama Models: $(command -v ollama &> /dev/null && {
        models_status=""
        if ollama list | grep -q "gemma3:1b"; then
            models_status="✓ gemma3:1b"
        else
            models_status="✗ gemma3:1b missing"
        fi
        if ollama list | grep -q "gemma3:27b"; then
            models_status="$models_status, ✓ gemma3:27b"
        else
            models_status="$models_status, ✗ gemma3:27b missing"
        fi
        echo "$models_status"
    } || echo "✗ Ollama not available")"
    
    # Check for enhanced RAG availability
    if [ -d "$PROJECT_ROOT/agriculture_embeddings" ]; then
        echo -e "Enhanced RAG Mode: ✓ Available (embeddings database found)"
    else
        echo -e "Enhanced RAG Mode: ✗ Unavailable (embeddings database not found)"
        echo -e "  Note: Place your embeddings in $PROJECT_ROOT/agriculture_embeddings/"
    fi
=======
    echo -e "Ollama Model: $(command -v ollama &> /dev/null && ollama list | grep -q "gemma3:1b" && echo "✓ gemma3:1b ready" || echo "✗ Not available")"
>>>>>>> 4c50ca585c1b036becba0d3b754e883c5426d926
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
