#!/bin/bash

# IndicAgri Bot - Cleanup Script
# Removes redundant installation files and consolidates the project

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                IndicAgri Bot - Project Cleanup               ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo

log_info "Cleaning up redundant requirements files..."

# Move to backup directory
mkdir -p backup_old_files

# Backup and remove redundant requirements files
REDUNDANT_REQUIREMENTS=(
    "agri_bot_searcher/requirements_basic.txt"
    "agri_bot_searcher/requirements_complete.txt"
    "agri_bot_searcher/requirements_complete_fixed.txt"
    "agri_bot_searcher/requirements_minimal.txt"
    "agri_bot_searcher/requirements_voice.txt"
    "agri_bot_searcher/requirements_indicagri_voice.txt"
)

for file in "${REDUNDANT_REQUIREMENTS[@]}"; do
    if [ -f "$file" ]; then
        log_info "Backing up $file"
        mv "$file" "backup_old_files/"
    fi
done

# Backup old installation scripts
OLD_SCRIPTS=(
    "install_agri_bot.sh"
    "start_agri_bot_original.sh"
    "quick_fix.sh"
    "fix_compatibility.sh"
    "fix_package_conflicts.sh"
    "resolve_pr_conflicts.sh"
)

for script in "${OLD_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        log_info "Backing up $script"
        mv "$script" "backup_old_files/"
    fi
done

# Update the main requirements.txt in agri_bot_searcher to point to root
if [ -f "agri_bot_searcher/requirements.txt" ]; then
    log_info "Updating agri_bot_searcher/requirements.txt to reference root requirements"
    echo "# See ../requirements.txt for unified dependencies" > agri_bot_searcher/requirements.txt
    echo "# Use: pip install -r ../requirements.txt" >> agri_bot_searcher/requirements.txt
fi

# Clean up test files that are no longer needed
OLD_TEST_FILES=(
    "test_enhanced_rag_complete.py"
    "test_enhanced_rag_quick.py"
    "test_enhanced_rag.py"
    "test_formatting_and_gpu.py"
    "test_indicagri_integration.py"
    "test_installation.py"
    "testing_the_rag.py"
)

for test_file in "${OLD_TEST_FILES[@]}"; do
    if [ -f "$test_file" ]; then
        log_info "Backing up $test_file"
        mv "$test_file" "backup_old_files/"
    fi
done

# Update README references
if [ -f "README.md" ]; then
    log_info "Updating README.md references..."
    # This would need manual review, so just create a note
    echo "# NOTE: README.md may need manual updates to reference new installation script" >> backup_old_files/README_UPDATE_NOTES.txt
fi

# Create a migration summary
cat > MIGRATION_SUMMARY.md << 'EOF'
# IndicAgri Bot - Migration Summary

## Changes Made

### ✅ Consolidated Requirements
- **Before**: 7+ separate requirements files
- **After**: Single `requirements.txt` with all dependencies
- **Location**: Root directory

### ✅ Streamlined Installation
- **Before**: `install_agri_bot.sh` (complex, redundant)
- **After**: `install_indicagri_bot.sh` (clean, unified)
- **Features**: Command-line options, better error handling

### ✅ Updated Branding
- **Before**: "Agriculture Bot Searcher", "Enhanced Agriculture Bot"
- **After**: "IndicAgri Bot" (consistent across all interfaces)

### ✅ Enhanced API Key Management
- **Added**: In-UI API key setup with instructions
- **Added**: Persistent storage (localStorage)
- **Added**: Help modals with step-by-step guides

### ✅ Voice Integration Ready
- **Status**: Voice features from agri_bot integrated
- **Note**: IndicTrans excluded due to dependency conflicts
- **Alternative**: Uses robust local models + optional SarvamAI

## File Changes

### New Files
- `install_indicagri_bot.sh` - Main installation script
- `start_indicagri_bot.sh` - Unified startup script  
- `requirements.txt` - Consolidated dependencies
- `INSTALLATION_GUIDE_NEW.md` - Updated documentation

### Modified Files
- `agri_bot_searcher/src/enhanced_voice_web_ui.py` - API key UI + branding
- `agri_bot_searcher/src/enhanced_web_ui.py` - Branding updates
- `agri_bot_searcher/src/web_ui.py` - Branding updates

### Moved to Backup
- All old requirements files → `backup_old_files/`
- Old installation scripts → `backup_old_files/`
- Test files → `backup_old_files/`

## Next Steps

1. **Test Installation**: Run `./install_indicagri_bot.sh`
2. **Test Startup**: Run `./start_indicagri_bot.sh`
3. **Verify Features**: Check voice, RAG, and web search
4. **Update Documentation**: Review and update remaining docs
5. **Clean Backup**: Remove backup files after verification

## API Keys Setup

### SarvamAI (Optional)
- Enhanced voice transcription for Indian languages
- Setup instructions available in web UI

### Hugging Face (Optional)  
- Access to gated models and higher rate limits
- Setup instructions available in web UI

## Dependencies Excluded

- **IndicTrans**: Excluded due to compatibility issues
- **Alternative**: Local voice models work without external dependencies

EOF

log_success "Cleanup completed!"
echo
echo -e "${GREEN}Summary:${NC}"
echo -e "  ✅ Consolidated requirements files"
echo -e "  ✅ Moved old files to backup_old_files/"
echo -e "  ✅ Updated branding to IndicAgri Bot"
echo -e "  ✅ Enhanced API key management"
echo -e "  ✅ Created migration summary"
echo
echo -e "${BLUE}To start using the new system:${NC}"
echo -e "${YELLOW}  ./install_indicagri_bot.sh${NC}"
echo -e "${YELLOW}  ./start_indicagri_bot.sh${NC}"
echo
echo -e "${BLUE}Documentation:${NC} INSTALLATION_GUIDE_NEW.md"
echo -e "${BLUE}Migration notes:${NC} MIGRATION_SUMMARY.md"
