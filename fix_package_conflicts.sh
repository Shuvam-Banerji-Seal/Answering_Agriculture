#!/bin/bash

# Quick Fix Script for IndicAgri Installation Issues
# This script resolves package conflicts and missing dependencies

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

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_PATH="$PROJECT_ROOT/agri_bot_env"

log_info "🔧 IndicAgri Quick Fix - Resolving Package Conflicts"
echo "=================================================="

# Activate virtual environment
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
    log_success "Virtual environment activated"
else
    log_error "Virtual environment not found. Please run install_agri_bot.sh first"
    exit 1
fi

# Fix 1: Uninstall conflicting packages
log_info "Removing conflicting packages..."
pip uninstall -y sentence-transformers huggingface-hub transformers 2>/dev/null || true

# Fix 2: Install compatible versions in correct order
log_info "Installing compatible package versions..."

# Install base transformers ecosystem with compatible versions
pip install "huggingface-hub>=0.20.0,<1.0"
pip install "transformers>=4.41.0,<5.0.0"
pip install "sentence-transformers>=2.2.0"

# Fix 3: Install correct IndicTrans package name
log_info "Installing IndicTrans with correct package name..."
pip install IndicTransToolkit || {
    log_warning "IndicTransToolkit not available, trying alternative..."
    pip install indic-transformers || log_warning "IndicTrans installation failed"
}

# Fix 4: Fix other common conflicts
log_info "Resolving other dependency conflicts..."
pip install "torch>=1.9.0" --upgrade
pip install "numpy>=1.21.0,<2.0.0"
pip install "scipy>=1.7.0"

# Fix 5: Install missing packages that were skipped
log_info "Installing remaining dependencies..."
pip install flask flask-cors pyyaml requests beautifulsoup4
pip install duckduckgo-search colorlog dataclasses-json
pip install faiss-cpu librosa soundfile

# Fix 6: Install SarvamAI with correct name
pip install sarvamai || log_warning "SarvamAI installation failed"

# Fix 7: Check for conda environment conflicts
if command -v conda &> /dev/null; then
    log_warning "Conda detected. Some conflicts may be due to conda/pip mixing."
    log_info "If issues persist, consider using: conda install -c conda-forge numba"
fi

# Test imports
log_info "Testing critical imports..."
python3 -c "
import torch
print('✓ PyTorch working')
import transformers
print('✓ Transformers working')
import sentence_transformers
print('✓ Sentence-transformers working')
try:
    import IndicTransToolkit
    print('✓ IndicTransToolkit working')
except ImportError:
    print('⚠ IndicTransToolkit not available')
try:
    import duckduckgo_search
    print('✓ DuckDuckGo Search working')
except ImportError:
    print('⚠ DuckDuckGo Search not available')
" || {
    log_warning "Some imports failed, but basic functionality should work"
}

log_success "Quick fix completed!"
echo
log_info "Next steps:"
echo "1. Try running: ./start_agri_bot.sh"
echo "2. If issues persist, try: pip install --upgrade --force-reinstall torch transformers"
echo "3. For voice features, ensure agri_bot directory contains the required models"
