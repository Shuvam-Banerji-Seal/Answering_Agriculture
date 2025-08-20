# Voice-Enabled Agriculture Bot Searcher - Setup Guide

This guide will help you set up the enhanced Agriculture Bot Searcher with voice transcription capabilities for Indian languages.

## 🎯 Overview

The enhanced system now supports:
- **Text Input**: Traditional text-based queries
- **Voice Input**: Indian language speech-to-text with English translation
- **Multiple Models**: AI4Bharat Conformer, IndicTrans2, and SarvamAI
- **10 Indian Languages**: Hindi, Marathi, Bengali, Telugu, Tamil, Gujarati, Kannada, Malayalam, Punjabi, Odia

## 📋 Prerequisites

### System Requirements
- Python 3.8+ (3.9+ recommended)
- CUDA-compatible GPU (recommended for better performance)
- At least 8GB RAM (16GB+ recommended)
- 10GB+ free disk space for models

### Operating System
- Linux (Ubuntu 18.04+, CentOS 7+)
- Windows 10/11 with WSL2 (recommended)
- macOS 10.15+ (CPU-only support)

## 🚀 Installation Steps

### Step 1: Environment Setup

```bash
# Create a new conda environment (recommended)
conda create -n agri-voice python=3.9
conda activate agri-voice

# Or use virtualenv
python -m venv agri-voice-env
source agri-voice-env/bin/activate  # Linux/Mac
# agri-voice-env\Scripts\activate   # Windows
```

### Step 2: Install PyTorch (CUDA-enabled)

```bash
# For CUDA 11.8 (check your CUDA version first)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CPU-only (slower but compatible)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# Verify installation
python -c "import torch; print(f'PyTorch: {torch.__version__}, CUDA: {torch.cuda.is_available()}')"
```

### Step 3: Install Core Dependencies

```bash
# Navigate to the agri_bot_searcher directory
cd agri_bot_searcher

# Install voice-enabled requirements
pip install -r requirements_voice.txt

# Install additional dependencies that may not be in PyPI
pip install git+https://github.com/AI4Bharat/IndicTrans2.git
```

### Step 4: Install NeMo Toolkit

```bash
# Install NeMo with ASR support
pip install nemo-toolkit[asr]

# If you encounter issues, try:
# conda install -c conda-forge nemo-toolkit
```

### Step 5: Model Setup

#### A. Download AI4Bharat Conformer Model

```bash
# Create models directory
mkdir -p models

# Download the Conformer model (replace with actual download link)
# Option 1: Direct download (if available)
wget -O models/conformer.nemo "https://example.com/conformer_model.nemo"

# Option 2: Use HuggingFace Hub
python -c "
from huggingface_hub import hf_hub_download
import os
os.makedirs('models', exist_ok=True)
# Download specific model - replace with actual model path
# model_path = hf_hub_download(repo_id='ai4bharat/conformer-hi-gpu', filename='model.nemo')
print('Model download setup complete')
"
```

#### B. Set up IndicTrans2

The IndicTrans2 model will be automatically downloaded when first used. Make sure you have sufficient disk space (~2GB).

#### C. Configure SarvamAI (Optional but Recommended)

```bash
# Get API key from https://sarvam.ai/
# Create .env file
echo "SARVAM_API_KEY=your_api_key_here" > .env

# Or set environment variable
export SARVAM_API_KEY="your_api_key_here"
```

### Step 6: Install Ollama

```bash
# Install Ollama for the search backend
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# In another terminal, pull required models
ollama pull llama2
ollama pull codellama
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `agri_bot_searcher` directory:

```bash
# SarvamAI API Key (for advanced transcription)
SARVAM_API_KEY=your_sarvam_api_key

# HuggingFace Token (for model downloads)
HUGGINGFACE_TOKEN=your_hf_token

# Model paths
CONFORMER_MODEL_PATH=./models/conformer.nemo

# Ollama configuration
OLLAMA_BASE_PORT=11434
OLLAMA_NUM_AGENTS=2
```

### Model Configuration

Edit `config.yml` to customize model settings:

```yaml
voice_transcription:
  primary_service: "sarvam"  # "sarvam" or "conformer"
  fallback_enabled: true
  supported_languages:
    - hi  # Hindi
    - mr  # Marathi
    - bn  # Bengali
    - te  # Telugu
    - ta  # Tamil
    - gu  # Gujarati
    - kn  # Kannada
    - ml  # Malayalam
    - pa  # Punjabi
    - or  # Odia

models:
  conformer:
    path: "./models/conformer.nemo"
    device: "cuda"  # or "cpu"
  
  indic_trans:
    model_name: "ai4bharat/indictrans2-indic-en-dist-200M"
    device: "cuda"  # or "cpu"
    
ollama:
  base_port: 11434
  models:
    - "llama2"
    - "codellama"
```

## 🎯 Testing the Installation

### 1. Test Voice Transcription Module

```bash
python -c "
from src.voice_transcription import create_transcriber
transcriber = create_transcriber()
print('Voice Transcriber Status:')
status = transcriber.is_model_ready()
for model, ready in status.items():
    print(f'  {model}: {\"✓\" if ready else \"✗\"}')
print('\\nSupported Languages:')
for code, info in transcriber.get_supported_languages().items():
    print(f'  {code}: {info[\"name\"]}')
"
```

### 2. Test Web Interface

```bash
# Start the voice-enabled web interface
python src/voice_web_ui.py

# Open browser and go to: http://localhost:5000
```

### 3. Test Individual Components

```bash
# Test basic chatbot functionality
python src/agriculture_chatbot.py

# Test with a simple query
python -c "
from src.agriculture_chatbot import AgricultureChatbot
bot = AgricultureChatbot()
result = bot.answer_query('What is the best fertilizer for wheat?')
print(result['answer'])
"
```

## 🚀 Running the Application

### Start All Services

```bash
# 1. Start Ollama (in one terminal)
ollama serve

# 2. Start the voice-enabled web interface (in another terminal)
cd agri_bot_searcher
python src/voice_web_ui.py

# 3. Open your browser and navigate to:
# http://localhost:5000
```

### Using the Interface

1. **Text Input**: Type your agricultural query in the text box
2. **Voice Input**: 
   - Select your language from the dropdown
   - Click the microphone button to start recording
   - Speak your query clearly
   - Click again to stop recording
   - The system will transcribe and translate your speech

3. **File Upload**: Upload pre-recorded audio files for transcription

## 🔧 Advanced Configuration

### GPU Memory Optimization

If you're running on limited GPU memory:

```python
# In voice_transcription.py, modify the model loading:
model = AutoModelForSeq2SeqLM.from_pretrained(
    model_name,
    trust_remote_code=True,
    torch_dtype=torch.float16,  # Use half precision
    device_map="auto",          # Automatic device mapping
    low_cpu_mem_usage=True      # Reduce CPU memory usage
)
```

### Performance Tuning

```bash
# Set environment variables for better performance
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
export TOKENIZERS_PARALLELISM=false
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. CUDA Out of Memory
```bash
# Reduce batch size or use CPU
export CUDA_VISIBLE_DEVICES=""  # Force CPU usage
```

#### 2. NeMo Installation Issues
```bash
# Try conda installation instead
conda install -c conda-forge nemo-toolkit
```

#### 3. IndicTrans Download Fails
```bash
# Manual installation
git clone https://github.com/AI4Bharat/IndicTrans2.git
cd IndicTrans2
pip install -e .
```

#### 4. Audio Recording Not Working
- Check browser permissions for microphone access
- Ensure you're using HTTPS or localhost
- Test with a different browser

#### 5. Model Loading Errors
```bash
# Check model paths and permissions
ls -la models/
# Verify CUDA installation
nvidia-smi
```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📱 Mobile Support

The web interface is responsive and works on mobile devices, but voice recording requires:
- HTTPS connection (for microphone access)
- Modern browser with Web Audio API support

## 🔄 Updates and Maintenance

### Regular Updates
```bash
# Update dependencies
pip install -r requirements_voice.txt --upgrade

# Pull latest Ollama models
ollama pull llama2:latest
```

### Model Updates
- Check AI4Bharat releases for newer Conformer models
- Update IndicTrans2 periodically for improvements

## 📊 Performance Expectations

### Processing Times (approximate)
- **SarvamAI**: 2-5 seconds for 30-second audio
- **Conformer + IndicTrans**: 5-15 seconds for 30-second audio
- **Text Query Processing**: 10-30 seconds depending on complexity

### Accuracy
- **SarvamAI**: 85-95% accuracy across languages
- **Conformer**: 80-90% accuracy (varies by language)
- **Translation**: 85-95% accuracy for agricultural terms

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review logs for error messages
3. Ensure all dependencies are correctly installed
4. Verify model files are properly downloaded
5. Check GPU/CUDA compatibility

For additional help, refer to:
- [NeMo Documentation](https://docs.nvidia.com/deeplearning/nemo/user-guide/docs/en/stable/)
- [IndicTrans2 GitHub](https://github.com/AI4Bharat/IndicTrans2)
- [SarvamAI Documentation](https://docs.sarvam.ai/)

## 🎉 Success!

If everything is working correctly, you should see:
- ✓ Voice transcription working in multiple Indian languages
- ✓ Automatic translation to English
- ✓ Integration with the agriculture search system
- ✓ Real-time web interface with both text and voice input

Happy farming! 🌾🚜
