#!/bin/bash
# Quick Fix Script for IndicAgri Installation Issues

set -e

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

log_info "🔧 IndicAgri Installation Quick Fix"
log_info "=================================="

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/agri_bot_env"

# Activate virtual environment
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
    log_success "Virtual environment activated"
else
    log_error "Virtual environment not found. Please run install_agri_bot.sh first"
    exit 1
fi

# Fix 1: Remove problematic packages
log_info "Fixing package conflicts..."
pip uninstall -y faiss-gpu 2>/dev/null || true

# Fix 2: Install correct packages
log_info "Installing correct package versions..."

# Install compatible huggingface_hub
pip install "huggingface_hub>=0.23.0,<1.0" --force-reinstall

# Install compatible transformers
pip install "transformers>=4.20.0,<4.35.0" --force-reinstall

# Install faiss-cpu (more compatible than GPU version)
pip install faiss-cpu>=1.7.0

# Install correct IndicTrans package
pip install IndicTransToolkit || log_warning "IndicTransToolkit may need manual installation"

# Install SarvamAI with correct name
pip install sarvamai || log_warning "SarvamAI installation failed"

# Fix 3: Install essential packages for IndicAgri
log_info "Installing essential IndicAgri packages..."
pip install flask flask-cors
pip install duckduckgo-search>=3.8.0
pip install sentence-transformers
pip install torch torchaudio --upgrade

# Fix 4: Install audio processing (optional)
log_info "Installing audio processing packages..."
pip install librosa soundfile || log_warning "Audio packages failed - voice features may not work"

# Fix 5: Test imports
log_info "Testing critical imports..."
python3 -c "
import torch
import flask
import sentence_transformers
import transformers
print('✓ Core packages imported successfully')
" || log_error "Import test failed"

log_success "Quick fix completed!"
log_info "You can now try running: ./start_agri_bot.sh"
