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
<<<<<<< HEAD
=======
RAG_ENABLED=true  # Default to true, but will be asked during installation
OLLAMA_MODEL="gemma3:1b"  # Default model, can be changed during installation

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --rag)
                RAG_ENABLED=true
                RAG_SET_VIA_CLI=true
                log_info "RAG system enabled via command line"
                shift
                ;;
            --no-rag)
                RAG_ENABLED=false
                RAG_SET_VIA_CLI=true
                log_info "RAG system disabled via command line"
                shift
                ;;
            --voice)
                VOICE_ENABLED=true
                log_info "Voice support enabled via command line"
                shift
                ;;
            --no-voice)
                VOICE_ENABLED=false
                log_info "Voice support disabled via command line"
                shift
                ;;
            --model)
                OLLAMA_MODEL="$2"
                MODEL_SET_VIA_CLI=true
                log_info "LLM model set to: $OLLAMA_MODEL"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown argument: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Show help information
show_help() {
    echo -e "${BLUE}IndicAgri Bot Installation Script${NC}"
    echo
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  --rag           Enable Enhanced RAG system (Qwen model, ~15GB)"
    echo "  --no-rag        Disable RAG system (lightweight, web search only)"
    echo "  --voice         Enable voice transcription support"
    echo "  --no-voice      Disable voice transcription support"
    echo "  --model MODEL   Set LLM model (default: gemma3:1b)"
    echo "                  Popular options: gemma3:1b, gemma3:7b, llama3.2:1b, llama3.2:3b"
    echo "  -h, --help      Show this help message"
    echo
    echo "If no RAG or model option is specified, you will be prompted during installation."
    echo
    echo "Examples:"
    echo "  $0                           # Interactive installation"
    echo "  $0 --rag --voice            # Full installation with RAG and voice"
    echo "  $0 --no-rag --model llama3.2:1b  # Lightweight installation with Llama model"
}

# User prompt for RAG installation (only if not specified via command line)
prompt_rag_installation() {
    # Skip prompt if RAG was already set via command line
    if [[ "${RAG_SET_VIA_CLI:-false}" == "true" ]]; then
        return
    fi
    
    echo
    echo -e "${YELLOW}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║                    RAG System Installation                   ║${NC}"
    echo -e "${YELLOW}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${BLUE}The Enhanced RAG system includes:${NC}"
    echo -e "  • Advanced document retrieval from agriculture knowledge base"
    echo -e "  • Qwen/Qwen3-Embedding-8B model (large, high-quality embeddings)"
    echo -e "  • FAISS vector similarity search"
    echo -e "  • Sub-query generation and answer synthesis"
    echo
    echo -e "${YELLOW}⚠️  WARNING: The Qwen model is approximately 15GB and requires:${NC}"
    echo -e "  • At least 16GB RAM for optimal performance"
    echo -e "  • 20GB+ free disk space"
    echo -e "  • Good internet connection for initial download"
    echo
    echo -e "${GREEN}Alternative: Without RAG, you'll have:${NC}"
    echo -e "  • Basic web search functionality"
    echo -e "  • Lightweight operation (< 2GB)"
    echo -e "  • Faster startup and response times"
    echo
    read -p "Do you want to install the Enhanced RAG system? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        RAG_ENABLED=true
        log_info "Enhanced RAG system will be installed"
    else
        RAG_ENABLED=false
        log_warning "RAG system will be skipped - only basic web search will be available"
    fi
}

# User prompt for LLM model selection (only if not specified via command line)
prompt_llm_model_selection() {
    # Skip prompt if model was already set via command line
    if [[ "${MODEL_SET_VIA_CLI:-false}" == "true" ]]; then
        return
    fi
    
    echo
    echo -e "${YELLOW}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║                    LLM Model Selection                       ║${NC}"
    echo -e "${YELLOW}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${BLUE}Choose an LLM model for the agriculture bot:${NC}"
    echo
    echo -e "${GREEN}Available models:${NC}"
    echo -e "  1) gemma3:1b    (1.2GB) - Default, fast, good for basic queries"
    echo -e "  2) gemma3:7b    (4.8GB) - Better quality, slower responses"
    echo -e "  3) llama3.2:1b  (1.3GB) - Fast, good general knowledge"
    echo -e "  4) llama3.2:3b  (2.0GB) - Balanced performance and quality"
    echo -e "  5) qwen2.5:1.5b (0.9GB) - Lightweight, good for agriculture"
    echo -e "  6) Custom model (enter your own)"
    echo
    echo -e "${YELLOW}💡 Recommendation:${NC} Use gemma3:1b for most users (default)"
    echo
    
    while true; do
        read -p "Select a model [1-6] (default: 1): " choice
        
        case $choice in
            "" | "1")
                OLLAMA_MODEL="gemma3:1b"
                log_info "Selected model: gemma3:1b (default)"
                break
                ;;
            "2")
                OLLAMA_MODEL="gemma3:7b"
                log_info "Selected model: gemma3:7b"
                break
                ;;
            "3")
                OLLAMA_MODEL="llama3.2:1b"
                log_info "Selected model: llama3.2:1b"
                break
                ;;
            "4")
                OLLAMA_MODEL="llama3.2:3b"
                log_info "Selected model: llama3.2:3b"
                break
                ;;
            "5")
                OLLAMA_MODEL="qwen2.5:1.5b"
                log_info "Selected model: qwen2.5:1.5b"
                break
                ;;
            "6")
                read -p "Enter custom model name (e.g., mistral:7b): " custom_model
                if [[ -n "$custom_model" ]]; then
                    OLLAMA_MODEL="$custom_model"
                    log_info "Selected custom model: $custom_model"
                    break
                else
                    log_warning "Invalid model name. Please try again."
                fi
                ;;
            *)
                log_warning "Invalid choice. Please select 1-6."
                ;;
        esac
    done
}
>>>>>>> 34a68fb (fixed .sh fails)

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

<<<<<<< HEAD
# Install base Python dependencies
=======
# Install base Python dependencies with or without RAG support
>>>>>>> 34a68fb (fixed .sh fails)
install_base_dependencies() {
    log_info "Installing base Python dependencies..."
    
    source "$VENV_PATH/bin/activate"
    
<<<<<<< HEAD
    # Always install critical dependencies first
    log_info "Installing critical core packages..."
    pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
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
    
    # Install from requirements file if available
    if [ -f "$AGRI_BOT_PATH/requirements.txt" ]; then
        log_info "Installing additional dependencies from requirements.txt..."
        pip install -r "$AGRI_BOT_PATH/requirements.txt"
    fi
    
    # Install complete requirements if available
    if [ -f "$AGRI_BOT_PATH/requirements_complete.txt" ]; then
                        log_info "Installing complete dependencies..."
        pip install -r "$AGRI_BOT_PATH/requirements_complete.txt" || {
            log_warning "Some packages from complete requirements failed, continuing..."
        }
    fi
    
    # Install RAG-specific dependencies
    log_info "Installing Enhanced RAG dependencies..."
    pip install sentence-transformers>=2.2.0 faiss-cpu>=1.7.0 || {
        log_warning "Some RAG dependencies failed to install"
    }
    
    log_success "Base dependencies installed"
=======
    # Always install core packages
    install_core_packages
    
    # Conditionally install RAG packages
    if [ "$RAG_ENABLED" = "true" ]; then
        install_rag_packages
    else
        install_lightweight_packages
    fi
    
    # Install additional packages from requirements files
    install_requirements_files
    
    log_success "Base dependencies installed successfully"
}

# Install core packages needed for all configurations
install_core_packages() {
    log_info "Installing core packages..."
    
    # Step 1: Install PyTorch with CPU support (lightweight for basic functionality)
    if [ "$RAG_ENABLED" = "true" ]; then
        log_info "Installing PyTorch for RAG support..."
        pip install torch==2.2.0+cpu torchvision==0.17.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
    else
        log_info "Installing lightweight PyTorch..."
        pip install torch==2.2.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
    fi
    
    # Step 2: Install core web and search packages (always needed)
    log_info "Installing web framework and search packages..."
    pip install "flask>=3.0.0" "flask-cors>=6.0.0" "pyyaml>=6.0"
    pip install "duckduckgo-search>=8.0.0" "requests>=2.28.0"
    pip install "ddgs"  # Additional DuckDuckGo search package
    pip install "beautifulsoup4>=4.9.3" "lxml>=4.6.3" "urllib3>=1.26.0"
    pip install "html5lib>=1.1" "dataclasses-json>=0.5.0" "colorlog>=6.0.0"
    
    # Step 3: Install numpy with compatible version
    pip install "numpy>=1.21.0,<2.0.0"
}

# Install RAG-specific packages (heavy dependencies)
install_rag_packages() {
    log_info "Installing Enhanced RAG system dependencies..."
    log_warning "This may take 10-20 minutes and requires significant disk space..."
    
    # Install transformers for Qwen support
    log_info "Installing transformers for Qwen model support..."
    pip install transformers>=4.55.0
    
    # Install huggingface-hub
    pip install "huggingface-hub>=0.20.0"
    
    # Install sentence-transformers for embeddings
    log_info "Installing sentence-transformers with Qwen model support..."
    pip install "sentence-transformers>=2.7.0"
    
    # Install FAISS for vector similarity search
    log_info "Installing FAISS for vector similarity search..."
    pip install faiss-cpu>=1.7.0
    
    # Test sentence-transformers installation with Qwen model
    log_info "Testing sentence-transformers installation with Qwen model..."
    log_warning "This will download the Qwen model (~15GB) - please be patient..."
    
    python3 -c "
import sys
try:
    import sentence_transformers
    print(f'✓ sentence-transformers version: {sentence_transformers.__version__}')
    
    from sentence_transformers import SentenceTransformer
    print('✓ SentenceTransformer class imported successfully')
    
    # Test Qwen model loading (the model used for creating embeddings)
    print('Loading Qwen/Qwen3-Embedding-8B model...')
    model = SentenceTransformer('Qwen/Qwen3-Embedding-8B')
    print('✓ Qwen3-Embedding-8B model loaded successfully')
    
    # Test encoding
    embeddings = model.encode(['Test sentence'])
    print(f'✓ Text encoding successful, shape: {embeddings.shape}')
    
except Exception as e:
    print(f'✗ sentence-transformers test failed: {e}')
    sys.exit(1)
" || {
        log_error "RAG system installation failed"
        log_warning "Falling back to lightweight installation..."
        RAG_ENABLED=false
        install_lightweight_packages
        return 1
    }
    
    log_success "Enhanced RAG system installed successfully"
}

# Install lightweight packages for basic functionality
install_lightweight_packages() {
    log_info "Installing lightweight packages for basic functionality..."
    
    # Install minimal transformers for basic NLP (optional)
    log_info "Installing basic transformers (lightweight)..."
    pip install transformers>=4.20.0 || log_warning "Basic transformers installation failed"
    
    # Install basic sentence-transformers without heavy models
    log_info "Installing basic sentence-transformers..."
    pip install sentence-transformers>=2.0.0 || log_warning "Basic sentence-transformers installation failed"
    
    # Test basic functionality
    python3 -c "
try:
    import requests
    import flask
    from duckduckgo_search import DDGS
    print('✓ Basic web search functionality available')
except Exception as e:
    print(f'✗ Basic functionality test failed: {e}')
    exit(1)
" || {
        log_error "Basic functionality test failed"
        return 1
    }
    
    log_success "Lightweight packages installed successfully"
}

# Install from various requirements files
install_requirements_files() {
    log_info "Installing additional dependencies from requirements files..."
    
    # Try minimal requirements first
    if [ -f "$AGRI_BOT_PATH/requirements_minimal.txt" ]; then
        log_info "Installing minimal dependencies..."
        pip install -r "$AGRI_BOT_PATH/requirements_minimal.txt" || log_warning "Some minimal requirements failed"
    elif [ -f "$AGRI_BOT_PATH/requirements_basic.txt" ]; then
        log_info "Installing basic dependencies..."
        pip install -r "$AGRI_BOT_PATH/requirements_basic.txt" || log_warning "Some basic requirements failed"
    elif [ -f "$AGRI_BOT_PATH/requirements.txt" ]; then
        log_info "Installing basic dependencies from requirements.txt..."
        pip install -r "$AGRI_BOT_PATH/requirements.txt" || log_warning "Some basic requirements failed"
    fi
    
    # Try complete requirements with error handling
    if [ -f "$AGRI_BOT_PATH/requirements_complete.txt" ]; then
        log_info "Attempting to install additional dependencies (with error handling)..."
        
        # Create a clean version of requirements_complete.txt without problematic packages
        create_clean_requirements
        
        # Install from cleaned requirements
        if [ -f "/tmp/requirements_clean.txt" ]; then
            pip install -r /tmp/requirements_clean.txt || log_warning "Some additional requirements failed"
            rm -f /tmp/requirements_clean.txt
        fi
    fi
}

# Create clean requirements file
create_clean_requirements() {
    log_info "Creating clean requirements file..."
    
    # Filter out problematic packages and version conflicts
    cat "$AGRI_BOT_PATH/requirements_complete.txt" | \
    grep -v "^<<<<<<< HEAD" | \
    grep -v "^=======" | \
    grep -v "^>>>>>>> " | \
    grep -v "indictrans-toolkit" | \
    grep -v "faiss-gpu" | \
    grep -v "torch==" | \
    grep -v "transformers==" | \
    grep -v "sentence-transformers==" | \
    grep -v "huggingface-hub==" | \
    grep -v "numpy==" > /tmp/requirements_clean.txt || true
    
    # Add compatible versions of core packages
    cat >> /tmp/requirements_clean.txt << EOF
# Core packages with compatible versions for Qwen model support
torch==2.2.0
transformers>=4.55.0
sentence-transformers>=2.7.0
huggingface-hub>=0.20.0
numpy>=1.21.0,<2.0.0
faiss-cpu==1.7.4
EOF
>>>>>>> 34a68fb (fixed .sh fails)
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
    
<<<<<<< HEAD
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
    if ollama list 2>/dev/null | grep -q "gemma3:1b"; then
        log_success "gemma3:1b model is ready for use"
    else
        log_warning "gemma3:1b model verification failed"
    fi
    
    if ollama list 2>/dev/null | grep -q "gemma3:27b"; then
        log_success "gemma3:27b model is ready for use"
    else
        log_info "gemma3:27b model not available - gemma3:1b will be used for synthesis"
    fi
}

# Install voice dependencies (NeMo, IndicTrans, etc.)
=======
    # Pull selected model with error handling
    log_info "Downloading $OLLAMA_MODEL model (this may take several minutes)..."
    if ollama list 2>/dev/null | grep -q "$OLLAMA_MODEL"; then
        log_warning "$OLLAMA_MODEL model already exists"
    else
        log_info "Downloading $OLLAMA_MODEL model... This may take 5-15 minutes depending on the model size and your connection."
        if ollama pull "$OLLAMA_MODEL"; then
            log_success "$OLLAMA_MODEL model downloaded successfully"
        else
            log_error "Failed to download $OLLAMA_MODEL model"
            log_warning "You can download it manually later with: ollama pull $OLLAMA_MODEL"
            
            # Fallback to gemma3:1b if the selected model fails
            if [[ "$OLLAMA_MODEL" != "gemma3:1b" ]]; then
                log_info "Attempting to download fallback model: gemma3:1b"
                if ollama pull gemma3:1b; then
                    log_success "Fallback model gemma3:1b downloaded successfully"
                    OLLAMA_MODEL="gemma3:1b"
                else
                    return 1
                fi
            else
                return 1
            fi
        fi
    fi
    
    # Pull gemma3:27b model for synthesis only if user selected a small model (optional but recommended)
    local model_size=""
    case "$OLLAMA_MODEL" in
        *:1b|*:1.5b)
            model_size="small"
            ;;
        *:3b|*:7b)
            model_size="medium"
            ;;
        *)
            model_size="large"
            ;;
    esac
    
    if [[ "$model_size" == "small" ]]; then
        log_info "Downloading gemma3:7b model for answer synthesis (recommended for better quality)..."
        if ollama list 2>/dev/null | grep -q "gemma3:7b"; then
            log_warning "gemma3:7b model already exists"
        else
            log_info "Downloading gemma3:7b model... This may take 10-15 minutes."
            if ollama pull gemma3:7b; then
                log_success "gemma3:7b model downloaded successfully"
            else
                log_warning "Failed to download gemma3:7b model. You can download it manually later with: ollama pull gemma3:7b"
                log_warning "The system will use $OLLAMA_MODEL as fallback for synthesis"
            fi
        fi
    fi
    
    # Verify selected model is available
    if ollama list 2>/dev/null | grep -q "$OLLAMA_MODEL"; then
        log_success "$OLLAMA_MODEL model is ready for use"
    else
        log_warning "$OLLAMA_MODEL model verification failed"
    fi
    
    # Check if synthesis model is available
    if ollama list 2>/dev/null | grep -q "gemma3:7b"; then
        log_success "gemma3:7b model is ready for synthesis"
    elif ollama list 2>/dev/null | grep -q "gemma3:27b"; then
        log_success "gemma3:27b model is ready for synthesis"
    else
        log_info "No synthesis model available - $OLLAMA_MODEL will be used for synthesis"
    fi
}

# Install voice dependencies (agri_bot integration)
>>>>>>> 34a68fb (fixed .sh fails)
install_voice_dependencies() {
    log_info "Installing voice transcription dependencies..."
    
    source "$VENV_PATH/bin/activate"
    
<<<<<<< HEAD
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

=======
    # Save current versions to avoid conflicts
    current_torch=$(pip show torch 2>/dev/null | grep Version | cut -d' ' -f2 || echo "none")
    current_transformers=$(pip show transformers 2>/dev/null | grep Version | cut -d' ' -f2 || echo "none")
    current_hf_hub=$(pip show huggingface-hub 2>/dev/null | grep Version | cut -d' ' -f2 || echo "none")
    current_sentence_transformers=$(pip show sentence-transformers 2>/dev/null | grep Version | cut -d' ' -f2 || echo "none")
    
    log_info "Current versions - torch: $current_torch, transformers: $current_transformers, huggingface-hub: $current_hf_hub, sentence-transformers: $current_sentence_transformers"
    
    # Check if voice requirements file exists in agri_bot_searcher
    if [ -f "$AGRI_BOT_PATH/requirements_voice.txt" ]; then
        log_info "Installing voice dependencies from requirements_voice.txt..."
        pip install -r "$AGRI_BOT_PATH/requirements_voice.txt" || log_warning "Some voice requirements failed"
    fi
    
    # Install agri_bot specific dependencies for voice transcription
    log_info "Installing agri_bot voice transcription dependencies..."
    
    # Save current directory
    current_dir=$(pwd)
    
    # Navigate to agri_bot directory and run its installation
    if [ -d "$PROJECT_ROOT/agri_bot" ]; then
        cd "$PROJECT_ROOT/agri_bot"
        
        # Make install script executable if needed
        if [ -f "install.sh" ]; then
            chmod +x install.sh
            
            log_info "Running agri_bot installation script with compatibility protection..."
            
            # Create a modified version of the install script that preserves our compatible versions
            create_compatible_agri_bot_install
            
            # Run the modified install script
            if bash install_compatible.sh; then
                log_success "agri_bot voice dependencies installed successfully"
            else
                log_warning "agri_bot installation script failed, continuing with manual installation"
                manual_voice_installation
            fi
        else
            log_warning "agri_bot install.sh not found, installing basic voice dependencies"
            manual_voice_installation
        fi
        
        # Return to original directory
        cd "$current_dir"
    else
        log_warning "agri_bot directory not found, installing basic voice dependencies"
        manual_voice_installation
    fi
    
    # Verify that sentence-transformers still works after voice installation
    log_info "Verifying sentence-transformers compatibility after voice installation..."
    python3 -c "
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print('✓ sentence-transformers still working after voice installation')
except Exception as e:
    print(f'✗ sentence-transformers broken after voice installation: {e}')
    raise
" || {
        log_error "sentence-transformers compatibility broken by voice installation"
        log_info "Reinstalling sentence-transformers..."
        pip install --force-reinstall sentence-transformers==2.2.2
    }
    
    log_success "Voice dependencies installation completed"
}

# Create compatible agri_bot install script
create_compatible_agri_bot_install() {
    log_info "Creating compatible agri_bot installation script..."
    
    cat > install_compatible.sh << 'EOF'
#!/bin/bash
# Compatible agri_bot installation that preserves sentence-transformers

set -e

echo "🔧 Installing agri_bot dependencies with compatibility protection..."

# Step 1: Install packaging if needed
pip install packaging

# Step 2: Check current versions and avoid downgrades
current_torch=$(pip show torch 2>/dev/null | grep Version | cut -d' ' -f2 || echo "none")
current_transformers=$(pip show transformers 2>/dev/null | grep Version | cut -d' ' -f2 || echo "none")
current_hf_hub=$(pip show huggingface-hub 2>/dev/null | grep Version | cut -d' ' -f2 || echo "none")
current_sentence_transformers=$(pip show sentence-transformers 2>/dev/null | grep Version | cut -d' ' -f2 || echo "none")

echo "Current versions: torch=$current_torch, transformers=$current_transformers, hf_hub=$current_hf_hub, sentence_transformers=$current_sentence_transformers"

# Step 3: Only install torch/transformers if not already compatible
if [[ "$current_torch" == "none" ]] || [[ "$current_torch" < "2.0.0" ]]; then
    echo "Installing/upgrading torch..."
    pip install torch>=2.2.0
else
    echo "Compatible torch already installed: $current_torch"
fi

if [[ "$current_transformers" == "none" ]] || [[ "$current_transformers" < "4.50.0" ]]; then
    echo "Installing/upgrading transformers..."
    pip install "transformers>=4.55.0"
else
    echo "Compatible transformers already installed: $current_transformers"
fi

# Step 4: Clone NeMo if not already present
if [ ! -d "NeMo" ]; then
    echo "Cloning NeMo repository..."
    git clone https://github.com/AI4Bharat/NeMo.git
fi

# Step 5: Install IndicTransToolkit (correct package name)
echo "Installing IndicTransToolkit..."
pip install IndicTransToolkit || {
    echo "IndicTransToolkit not available, trying alternatives..."
    pip install indictrans2 || echo "Warning: IndicTrans installation failed"
}

# Step 6: Install NeMo dependencies
echo "Installing NeMo dependencies..."
if [ -d "NeMo" ]; then
    cd NeMo
    if [ -f "reinstall.sh" ]; then
        bash reinstall.sh || echo "Warning: NeMo reinstall failed"
    else
        pip install -e . || echo "Warning: NeMo installation failed"
    fi
    cd ..
fi

# Step 7: Install sarvamai
echo "Installing sarvamai..."
pip install -U sarvamai || echo "Warning: sarvamai installation failed"

# Step 8: Install additional audio packages
echo "Installing audio processing packages..."
pip install librosa soundfile || echo "Warning: Some audio packages failed"

# Step 9: Fix numpy/pyarrow versions if needed
echo "Ensuring compatible numpy version..."
pip install "numpy>=1.21.0,<1.25.0" --upgrade

echo "✅ Compatible agri_bot setup complete!"
EOF

    chmod +x install_compatible.sh
}

# Manual voice installation fallback
manual_voice_installation() {
    log_info "Performing manual voice dependencies installation..."
    
    # Install basic voice dependencies without breaking existing packages
    pip install packaging
    
    # Install IndicTransToolkit
    pip install IndicTransToolkit || {
        log_warning "IndicTransToolkit not available, trying alternatives..."
        pip install indictrans2 || log_warning "No IndicTrans package available"
    }
    
    # Install SarvamAI
    pip install sarvamai || log_warning "SarvamAI installation failed"
    
    # Install audio processing
    pip install librosa soundfile || log_warning "Some audio packages failed"
    
    log_success "Manual voice dependencies installation completed"
}

>>>>>>> 34a68fb (fixed .sh fails)
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
<<<<<<< HEAD
# Agriculture Bot Environment Configuration
=======
# IndicAgri Bot Environment Configuration
>>>>>>> 34a68fb (fixed .sh fails)

# Hugging Face Token (optional, for advanced models)
# HUGGINGFACE_TOKEN=your_token_here

# SarvamAI API Key (optional, for voice transcription)
# SARVAM_API_KEY=your_api_key_here

# Voice transcription settings
VOICE_ENABLED=$VOICE_ENABLED
DEFAULT_VOICE_ENGINE=conformer

<<<<<<< HEAD
# Ollama settings
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma3:1b
=======
# RAG system settings
RAG_ENABLED=$RAG_ENABLED
RAG_MODEL=Qwen/Qwen3-Embedding-8B

# Ollama settings
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=$OLLAMA_MODEL
>>>>>>> 34a68fb (fixed .sh fails)

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

<<<<<<< HEAD
# Agriculture Bot Searcher Startup Script
=======
# IndicAgri Bot Startup Script
>>>>>>> 34a68fb (fixed .sh fails)

# Get the directory where this script is located (works regardless of where it's run from)
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="\$SCRIPT_DIR"
VENV_PATH="\$PROJECT_ROOT/agri_bot_env"
AGRI_BOT_PATH="\$PROJECT_ROOT/agri_bot_searcher"
EMBEDDINGS_PATH="\$PROJECT_ROOT/agriculture_embeddings"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

<<<<<<< HEAD
echo -e "\033[0;34mStarting Agriculture Bot Searcher...\033[0m"

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    source "$PROJECT_ROOT/.env"
=======
echo -e "\033[0;34mStarting IndicAgri Bot...\033[0m"

# Activate virtual environment
source "\$VENV_PATH/bin/activate"

# Load environment variables
if [ -f "\$PROJECT_ROOT/.env" ]; then
    source "\$PROJECT_ROOT/.env"
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
cd "$AGRI_BOT_PATH"

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
cd "\$AGRI_BOT_PATH"

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
if [ -d "\$EMBEDDINGS_PATH" ] && [ -f "\$AGRI_BOT_PATH/src/enhanced_rag_system.py" ] && [ "\$RAG_PACKAGES_INSTALLED" = "true" ]; then
    ENHANCED_AVAILABLE=true
fi

# Display startup information
if [ "\$RAG_PACKAGES_INSTALLED" = "true" ]; then
    echo -e "\${BLUE}RAG packages installed: sentence-transformers, FAISS\${NC}"
else
    echo -e "\${YELLOW}RAG packages not installed - lightweight mode only\${NC}"
fi

if [ -d "\$EMBEDDINGS_PATH" ]; then
    echo -e "\${BLUE}Embeddings database found: \$EMBEDDINGS_PATH\${NC}"
else
    echo -e "\${YELLOW}Embeddings database not found - web search only\${NC}"
fi

# Start appropriate mode
if [ "\$VOICE_ENABLED" = "true" ]; then
    echo -e "\${GREEN}Starting IndicAgri Bot with Voice Support\${NC}"
    python3 src/enhanced_voice_web_ui.py
elif [ "\$ENHANCED_AVAILABLE" = "true" ]; then
    echo -e "\${GREEN}Starting Enhanced IndicAgri Bot with RAG + Web Search\${NC}"
    echo -e "\${YELLOW}Features: Database retrieval, Web search, Sub-query generation, LLM synthesis\${NC}"
    python3 src/enhanced_web_ui.py
else
    echo -e "\${GREEN}Starting IndicAgri Bot (Lightweight Mode)\${NC}"
    if [ "\$RAG_PACKAGES_INSTALLED" = "false" ]; then
        echo -e "\${YELLOW}Note: RAG packages not installed. Using web search only.\${NC}"
    else
        echo -e "\${YELLOW}Note: Embeddings database not found. Using web search only.\${NC}"
    fi
>>>>>>> 34a68fb (fixed .sh fails)
    python3 src/web_ui.py
fi
EOF

    chmod +x "$PROJECT_ROOT/start_agri_bot.sh"
    log_success "Startup script created"
}

<<<<<<< HEAD
# Test basic functionality
=======
# Test basic functionality including sentence-transformers
>>>>>>> 34a68fb (fixed .sh fails)
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
<<<<<<< HEAD
    print('✓ PyTorch imported successfully')
=======
    print('✓ PyTorch imported successfully:', torch.__version__)
>>>>>>> 34a68fb (fixed .sh fails)
except ImportError as e:
    print(f'✗ PyTorch import failed: {e}')
    sys.exit(1)

try:
<<<<<<< HEAD
=======
    import transformers
    print('✓ Transformers imported successfully:', transformers.__version__)
except ImportError as e:
    print(f'✗ Transformers import failed: {e}')
    sys.exit(1)

try:
    import sentence_transformers
    print('✓ Sentence Transformers imported successfully:', sentence_transformers.__version__)
    
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(['Test sentence'])
    print(f'✓ Sentence Transformers working, embedding shape: {embeddings.shape}')
except ImportError as e:
    print(f'✗ Sentence Transformers import failed: {e}')
    sys.exit(1)

try:
    import faiss
    print('✓ FAISS imported successfully')
except ImportError as e:
    print(f'✗ FAISS import failed: {e}')
    sys.exit(1)

try:
>>>>>>> 34a68fb (fixed .sh fails)
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
<<<<<<< HEAD
=======

try:
    from enhanced_rag_system import DatabaseRetriever
    retriever = DatabaseRetriever()
    print('✓ RAG system initialized successfully')
except Exception as e:
    print(f'✗ RAG system initialization failed: {e}')
    sys.exit(1)
>>>>>>> 34a68fb (fixed .sh fails)
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
            
<<<<<<< HEAD
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
                
                # Test gemma3:27b if available
                if ollama list 2>/dev/null | grep -q "gemma3:27b"; then
                    log_info "Testing gemma3:27b model inference..."
                    if echo "Test" | ollama run gemma3:27b --format json > /dev/null 2>&1; then
                        log_success "gemma3:27b model is working correctly"
                    else
                        log_warning "gemma3:27b model inference test failed"
                    fi
                fi
            else
                log_warning "gemma3:1b model not found - attempting to download..."
                if ollama pull gemma3:1b; then
                    log_success "gemma3:1b model downloaded successfully"
                else
                    log_error "Failed to download gemma3:1b model"
=======
            # Check if selected model exists
            if ollama list 2>/dev/null | grep -q "$OLLAMA_MODEL"; then
                log_success "$OLLAMA_MODEL model is available"
                
                # Test model inference
                log_info "Testing model inference..."
                if echo "Hello" | ollama run "$OLLAMA_MODEL" --format json > /dev/null 2>&1; then
                    log_success "$OLLAMA_MODEL model is working correctly"
                else
                    log_warning "$OLLAMA_MODEL model inference test failed"
                fi
                
                # Test synthesis model if available
                if ollama list 2>/dev/null | grep -q "gemma3:7b"; then
                    log_info "Testing gemma3:7b synthesis model inference..."
                    if echo "Test" | ollama run gemma3:7b --format json > /dev/null 2>&1; then
                        log_success "gemma3:7b synthesis model is working correctly"
                    else
                        log_warning "gemma3:7b synthesis model inference test failed"
                    fi
                elif ollama list 2>/dev/null | grep -q "gemma3:27b"; then
                    log_info "Testing gemma3:27b synthesis model inference..."
                    if echo "Test" | ollama run gemma3:27b --format json > /dev/null 2>&1; then
                        log_success "gemma3:27b synthesis model is working correctly"
                    else
                        log_warning "gemma3:27b synthesis model inference test failed"
                    fi
                fi
            else
                log_warning "$OLLAMA_MODEL model not found - attempting to download..."
                if ollama pull "$OLLAMA_MODEL"; then
                    log_success "$OLLAMA_MODEL model downloaded successfully"
                else
                    log_error "Failed to download $OLLAMA_MODEL model"
>>>>>>> 34a68fb (fixed .sh fails)
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
<<<<<<< HEAD
    echo -e "${BLUE}Agriculture Bot Searcher - Complete Installation${NC}"
    echo "=============================================="
    
    check_system_requirements
=======
    echo -e "${BLUE}IndicAgri Bot - Complete Installation${NC}"
    echo "=========================================="
    
    # Parse command line arguments first
    parse_arguments "$@"
    
    check_system_requirements
    prompt_rag_installation  # Ask user about RAG installation (if not set via CLI)
    prompt_llm_model_selection  # Ask user about LLM model selection (if not set via CLI)
>>>>>>> 34a68fb (fixed .sh fails)
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
=======
    echo -e "RAG System: $([ "$RAG_ENABLED" = "true" ] && echo "✓ Enhanced (Qwen model)" || echo "✗ Lightweight (web search only)")"
>>>>>>> 34a68fb (fixed .sh fails)
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
<<<<<<< HEAD
    if [ -d "$PROJECT_ROOT/agriculture_embeddings" ]; then
        echo -e "Enhanced RAG Mode: ✓ Available (embeddings database found)"
    else
        echo -e "Enhanced RAG Mode: ✗ Unavailable (embeddings database not found)"
        echo -e "  Note: Place your embeddings in $PROJECT_ROOT/agriculture_embeddings/"
    fi
    echo
    echo -e "${BLUE}To start the application:${NC}"
=======
    if [ "$RAG_ENABLED" = "true" ]; then
        if [ -d "$PROJECT_ROOT/agriculture_embeddings" ]; then
            echo -e "Enhanced RAG Mode: ✓ Fully Available (Qwen model + embeddings database)"
        else
            echo -e "Enhanced RAG Mode: ⚠ Partially Available (Qwen model installed, embeddings database not found)"
            echo -e "  Note: Place your embeddings in $PROJECT_ROOT/agriculture_embeddings/"
        fi
    else
        echo -e "Enhanced RAG Mode: ✗ Not installed (lightweight mode selected)"
        echo -e "  Note: Re-run installer and select 'y' for RAG to enable advanced features"
    fi
    
    # Check for agri_bot integration
    if [ -d "$PROJECT_ROOT/agri_bot" ]; then
        echo -e "IndicAgri Voice Module: ✓ Available (agri_bot found)"
    else
        echo -e "IndicAgri Voice Module: ✗ Not available (agri_bot not found)"
    fi
    
    echo
    echo -e "${BLUE}To start IndicAgri Bot:${NC}"
>>>>>>> 34a68fb (fixed .sh fails)
    echo "cd $PROJECT_ROOT"
    echo "./start_agri_bot.sh"
    echo
    echo -e "${BLUE}Or manually:${NC}"
    echo "source $VENV_PATH/bin/activate"
    echo "cd $AGRI_BOT_PATH"
    if [ "$VOICE_ENABLED" = "true" ]; then
<<<<<<< HEAD
        echo "python3 src/voice_web_ui.py"
    else
        echo "python3 src/web_ui.py"
    fi
=======
        echo "python3 src/enhanced_voice_web_ui.py"
    elif [ "$RAG_ENABLED" = "true" ]; then
        echo "python3 src/enhanced_web_ui.py"
    else
        echo "python3 src/web_ui.py"
    fi
    
    echo
    echo -e "${GREEN}🎉 IndicAgri Bot installation complete!${NC}"
    if [ "$RAG_ENABLED" = "true" ]; then
        echo -e "${YELLOW}Enhanced RAG system with Qwen model is ready for high-quality retrieval.${NC}"
    else
        echo -e "${YELLOW}Lightweight installation complete - basic web search functionality available.${NC}"
    fi
>>>>>>> 34a68fb (fixed .sh fails)
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
<<<<<<< HEAD
main "$@"
=======
main "$@"
>>>>>>> 34a68fb (fixed .sh fails)
