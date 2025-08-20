#!/bin/bash
# Fix IndicTrans and sentence-transformers compatibility issues

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/agri_bot_env"

log_info "🔧 Fixing IndicTrans and sentence-transformers compatibility"
log_info "==========================================================="

# Activate virtual environment
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
    log_success "Virtual environment activated"
else
    log_error "Virtual environment not found at $VENV_PATH"
    exit 1
fi

# Step 1: Upgrade to compatible versions
log_info "Step 1: Installing compatible package versions..."

# Install compatible huggingface-hub and transformers
pip install "huggingface-hub>=0.20.0,<1.0" --upgrade
pip install "transformers>=4.41.0,<5.0.0" --upgrade

# Step 2: Try different IndicTrans packages
log_info "Step 2: Installing IndicTrans package..."

# Try multiple package names for IndicTrans
if pip install IndicTransToolkit; then
    log_success "IndicTransToolkit installed successfully"
elif pip install indictrans2; then
    log_success "indictrans2 installed successfully"
elif pip install ai4bharat-indictrans; then
    log_success "ai4bharat-indictrans installed successfully"
else
    log_warning "No IndicTrans package could be installed"
    log_info "Trying to install from GitHub..."
    if pip install git+https://github.com/AI4Bharat/IndicTrans2.git; then
        log_success "IndicTrans2 installed from GitHub"
    else
        log_error "Failed to install any IndicTrans package"
    fi
fi

# Step 3: Ensure sentence-transformers compatibility
log_info "Step 3: Ensuring sentence-transformers compatibility..."
pip install "sentence-transformers>=2.2.0" --upgrade

# Step 4: Test imports
log_info "Step 4: Testing critical imports..."

python3 -c "
import sys
success = True

try:
    import transformers
    print('✓ transformers imported successfully')
except ImportError as e:
    print(f'✗ transformers import failed: {e}')
    success = False

try:
    import sentence_transformers
    print('✓ sentence-transformers imported successfully')
except ImportError as e:
    print(f'✗ sentence-transformers import failed: {e}')
    success = False

try:
    import huggingface_hub
    print('✓ huggingface-hub imported successfully')
except ImportError as e:
    print(f'✗ huggingface-hub import failed: {e}')
    success = False

# Try IndicTrans imports
try:
    from IndicTransToolkit.processor import IndicProcessor
    print('✓ IndicTransToolkit imported successfully')
except ImportError:
    try:
        import indictrans2
        print('✓ indictrans2 imported successfully')
    except ImportError:
        print('⚠ No IndicTrans package available (voice features may be limited)')

if not success:
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    log_success "All critical packages imported successfully!"
    log_info "You can now try running: ./start_agri_bot.sh"
else
    log_error "Some package imports failed"
    exit 1
fi

log_success "Compatibility fix completed!"
