# IndicAgri Bot - Troubleshooting Guide

## Quick Fix for Installation Issues

If you encountered errors during installation, run this quick fix:

```bash
./quick_fix.sh
```

## Common Issues and Solutions

### 1. FAISS-GPU Installation Failed
**Error:** `ERROR: Could not find a version that satisfies the requirement faiss-gpu`

**Solution:** This is normal on systems without CUDA support. The installation script automatically falls back to faiss-cpu.

**Manual Fix:**
```bash
source agri_bot_env/bin/activate
pip uninstall faiss-gpu faiss-cpu
pip install faiss-cpu>=1.7.0
```

### 2. Git Merge Conflicts in Requirements
**Error:** `ERROR: Invalid requirement: '<<<<<<< HEAD'`

**Solution:** The requirements file had merge conflicts. Use the fixed version:
```bash
source agri_bot_env/bin/activate
pip install -r agri_bot_searcher/requirements_basic.txt
```

### 3. IndicTrans Package Not Found
**Error:** `ERROR: Could not find a version that satisfies the requirement indictrans-toolkit`

**Solution:** Use the correct package name:
```bash
source agri_bot_env/bin/activate
pip install IndicTransToolkit
```

### 4. Hugging Face Hub Version Conflict
**Error:** `transformers 4.55.2 requires huggingface-hub<1.0,>=0.34.0, but you have huggingface-hub 0.23.2`

**Solution:** Install compatible versions:
```bash
source agri_bot_env/bin/activate
pip install "huggingface_hub>=0.23.0,<1.0"
pip install "transformers>=4.20.0,<4.35.0"
```

### 5. Voice Transcription Not Available
**Issue:** Voice features don't work

**Solution:** Install additional voice dependencies:
```bash
source agri_bot_env/bin/activate
cd agri_bot
bash install.sh
```

## Verification Steps

### 1. Test Basic Installation
```bash
source agri_bot_env/bin/activate
python3 test_indicagri_integration.py
```

### 2. Test Web Interface
```bash
source agri_bot_env/bin/activate
cd agri_bot_searcher
python3 src/enhanced_voice_web_ui.py
```
Then open: http://localhost:5000

### 3. Test Voice Transcription
```bash
source agri_bot_env/bin/activate
cd agri_bot_searcher/src
python3 -c "from indicagri_voice_integration import IndicAgriVoiceTranscriber; t = IndicAgriVoiceTranscriber(); print('Voice available:', t.is_available())"
```

## Step-by-Step Recovery

If everything fails, follow these steps:

### 1. Clean Installation
```bash
# Remove virtual environment
rm -rf agri_bot_env

# Re-run installation
./install_agri_bot.sh
```

### 2. Minimal Installation
```bash
# Create virtual environment
python3 -m venv agri_bot_env
source agri_bot_env/bin/activate

# Install only essential packages
pip install flask flask-cors torch sentence-transformers faiss-cpu
pip install duckduckgo-search requests beautifulsoup4

# Test basic functionality
cd agri_bot_searcher
python3 src/web_ui.py
```

### 3. Manual Voice Setup (Advanced)
```bash
source agri_bot_env/bin/activate

# Install voice dependencies manually
pip install torch torchaudio transformers
pip install IndicTransToolkit
pip install sarvamai

# Test voice functionality
cd agri_bot
python3 -c "from new_bot import main; print('agri_bot available')"
```

## System Requirements

### Minimum Requirements
- Python 3.8+
- 4GB RAM
- 2GB free disk space
- Linux/Ubuntu (recommended)

### Recommended Requirements
- Python 3.9+
- 8GB RAM
- 5GB free disk space
- CUDA-capable GPU (optional, for faster processing)

### Required System Packages
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-dev python3-pip git curl ffmpeg

# For audio processing
sudo apt install portaudio19-dev python3-pyaudio
```

## Feature Availability

| Feature | Status | Requirements |
|---------|--------|-------------|
| Basic Chat | ✓ Always Available | Flask, torch, sentence-transformers |
| Web Search | ✓ Always Available | duckduckgo-search |
| Voice Input (UI) | ✓ Always Available | Browser microphone |
| Voice Transcription | ⚠️ Conditional | agri_bot modules, IndicTrans |
| Enhanced RAG | ⚠️ Conditional | agriculture_embeddings database |
| Multi-language | ⚠️ Conditional | IndicTransToolkit, NeMo |

## Getting Help

1. **Check Logs:** Look at terminal output during installation
2. **Run Tests:** Use `test_indicagri_integration.py`
3. **Try Quick Fix:** Run `./quick_fix.sh`
4. **Check Dependencies:** Verify all required packages are installed
5. **Start Simple:** Use basic web UI first, then add features

## Success Indicators

✅ **Installation Successful When:**
- No error messages during pip install
- Virtual environment activates without issues
- `./start_agri_bot.sh` starts without errors
- Web interface loads at http://localhost:5000
- Basic chat functionality works

✅ **Voice Features Working When:**
- Microphone permission granted in browser
- Voice transcription shows results
- Language selection works
- English translation appears

## Contact and Support

For additional help:
1. Check the repository issues
2. Review the installation logs
3. Ensure all system requirements are met
4. Try the minimal installation first
