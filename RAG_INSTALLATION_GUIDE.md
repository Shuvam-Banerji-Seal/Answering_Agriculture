# IndicAgri Bot RAG Installation Guide

## Overview

The IndicAgri Bot now supports two installation modes to accommodate different hardware capabilities:

### 🚀 **Enhanced RAG Mode** (Recommended for powerful systems)
- **Features**: Advanced document retrieval, Qwen/Qwen3-Embedding-8B model, FAISS vector search
- **Requirements**: 16GB+ RAM, 20GB+ disk space, good internet connection
- **Best for**: Production deployments, high-quality responses, research use

### 💻 **Lightweight Mode** (Recommended for laptops/limited resources)
- **Features**: Web search functionality, basic NLP capabilities
- **Requirements**: 4GB+ RAM, 2GB+ disk space
- **Best for**: Development, testing, resource-constrained environments

## Installation Options

### Interactive Installation (Default)
```bash
./install_agri_bot.sh
```
You'll be prompted to choose whether to install the RAG system.

### Command Line Options

#### Enhanced RAG Installation
```bash
./install_agri_bot.sh --rag
```

#### Lightweight Installation
```bash
./install_agri_bot.sh --no-rag
```

#### Full Installation with Voice Support
```bash
./install_agri_bot.sh --rag --voice
```

#### Lightweight with Voice Support
```bash
./install_agri_bot.sh --no-rag --voice
```

## System Requirements

### Enhanced RAG Mode
| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 12GB | 16GB+ |
| Storage | 20GB | 30GB+ |
| Internet | Stable | High-speed |
| CPU | 4 cores | 8+ cores |

### Lightweight Mode
| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 2GB | 4GB+ |
| Storage | 2GB | 5GB+ |
| Internet | Basic | Stable |
| CPU | 2 cores | 4+ cores |

## Features Comparison

| Feature | Enhanced RAG | Lightweight |
|---------|-------------|-------------|
| Web Search | ✅ | ✅ |
| Document Retrieval | ✅ | ❌ |
| Vector Embeddings | ✅ (Qwen3-8B) | ❌ |
| Sub-query Generation | ✅ | ❌ |
| Answer Synthesis | ✅ | ✅ (basic) |
| Voice Support | ✅ | ✅ |
| Startup Time | Slower | Fast |
| Memory Usage | High | Low |

## Installation Process

### Enhanced RAG Mode
1. Downloads and installs PyTorch, transformers, sentence-transformers
2. Downloads Qwen/Qwen3-Embedding-8B model (~15GB)
3. Installs FAISS for vector similarity search
4. Tests model loading and encoding capabilities
5. Sets up enhanced web UI with RAG integration

### Lightweight Mode
1. Installs minimal PyTorch and basic transformers
2. Installs web scraping and search tools
3. Sets up basic web UI with search functionality
4. Skips heavy ML models and vector databases

## Troubleshooting

### Enhanced RAG Mode Issues

**Problem**: "Out of memory" during model loading
**Solution**: 
- Ensure you have 16GB+ RAM
- Close other applications
- Try restarting and running only the bot

**Problem**: Model download takes too long
**Solution**:
- Check internet connection
- The Qwen model is ~15GB, download may take 30+ minutes
- Consider using lightweight mode for testing

**Problem**: "CUDA out of memory" error
**Solution**:
- The installation uses CPU-only versions
- If you see this error, restart the installation

### Lightweight Mode Issues

**Problem**: Limited response quality
**Solution**:
- This is expected in lightweight mode
- For better responses, use Enhanced RAG mode
- Ensure Ollama models are properly installed

## Switching Between Modes

To switch from lightweight to enhanced RAG:
```bash
./install_agri_bot.sh --rag
```

To switch from enhanced RAG to lightweight:
```bash
./install_agri_bot.sh --no-rag
```

The installer will preserve your existing virtual environment and only install/remove the necessary packages.

## Performance Tips

### Enhanced RAG Mode
- First startup will be slow (model loading)
- Subsequent startups are faster
- Query response time: 5-15 seconds
- Memory usage: 8-12GB

### Lightweight Mode
- Fast startup (< 30 seconds)
- Query response time: 2-5 seconds
- Memory usage: 1-2GB
- Limited to web search results

## Getting Help

For installation issues:
```bash
./install_agri_bot.sh --help
```

For runtime issues, check the logs in the terminal when starting the bot.
