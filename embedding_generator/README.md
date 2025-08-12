# Agriculture Embedding Generator

A comprehensive system for generating high-quality embeddings from Indian agriculture datasets using the Qwen3-Embedding-8B model.

## Overview

This repository contains a complete pipeline for processing agricultural text data and generating embeddings suitable for semantic search, RAG systems, and agricultural knowledge retrieval.

## Features

- **Advanced Text Processing**: Intelligent chunking with overlap for optimal context preservation
- **State-of-the-art Embeddings**: Uses Qwen3-Embedding-8B model for high-quality vector representations
- **FAISS Integration**: Fast similarity search with optimized indexing
- **Rich Metadata**: Preserves agricultural context (crops, soil types, climate, etc.)
- **Comprehensive Analytics**: Detailed statistics and dataset insights
- **Production Ready**: Robust error handling and progress tracking

## Architecture

```
Input JSONL → Text Chunking → Embedding Generation → FAISS Indexing → Output Storage
     ↓              ↓                ↓                    ↓              ↓
Agricultural    Overlapping     Qwen3-Embedding-8B    Vector Index    Embeddings +
   Dataset       Chunks           Model                              Metadata
```

## Quick Start

### Prerequisites

- Python 3.8+
- CUDA-capable GPU (recommended)
- 16GB+ RAM
- 10GB+ disk space

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd embedding_generator

# Install dependencies
pip install -r requirements.txt

# Or use the setup script
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Basic Usage

```bash
# Generate embeddings from your JSONL dataset
python src/create_embeddings.py --input data/your_dataset.jsonl --output embeddings_output

# Or use the convenience script
./scripts/generate_embeddings.sh data/your_dataset.jsonl
```

## Configuration

### Configuration Files

The system supports YAML configuration files for easy customization:

```bash
# Use the original Qwen3-Embedding-8B configuration
python src/create_embeddings.py --config config/qwen_config.yaml --input data.jsonl

# Use default configuration with all options
python src/create_embeddings.py --config config/default_config.yaml --input data.jsonl
```

### Available Configurations

- **`config/qwen_config.yaml`**: Matches the original setup that generated `agriculture_embeddings`
- **`config/default_config.yaml`**: Comprehensive configuration with all available options

### Model Configuration

The system uses Qwen3-Embedding-8B by default. You can customize via config file or command line:

```python
embedding_system = AgricultureEmbeddingSystem(
    model_name="Qwen/Qwen3-Embedding-8B",
    chunk_size=256,        # Tokens per chunk
    chunk_overlap=25,      # Overlap between chunks
    device="auto"          # auto, cuda, cpu
)
```

## Input Data Format

Expected JSONL format with agricultural metadata:

```json
{
  "title": "Sustainable Rice Farming in India",
  "text_extracted": "Full text content...",
  "abstract": "Research abstract...",
  "link": "https://example.com/paper",
  "source_domain": "example.com",
  "crop_types": ["rice", "wheat"],
  "farming_methods": ["sustainable", "organic"],
  "soil_types": ["alluvial soil", "black soil"],
  "climate_info": ["monsoon", "tropical"],
  "fertilizers": ["nitrogen", "phosphorus"],
  "tags": ["research", "sustainability"]
}
```

## Output Structure

```
embeddings_output/
├── embeddings.npy          # NumPy array of embeddings
├── faiss_index.bin         # FAISS index for similarity search
├── metadata.json           # Chunk metadata (human-readable)
├── metadata.pkl            # Chunk metadata (binary, faster loading)
├── config.json             # Generation configuration
└── summary_stats.json      # Dataset statistics
```

## Performance

### Benchmarks

- **Processing Speed**: ~50-100 records/minute (GPU)
- **Memory Usage**: ~8GB GPU memory for Qwen3-Embedding-8B
- **Index Build**: ~1M embeddings in 30 seconds
- **Search Speed**: <1ms per query (FAISS)

## License

MIT License - see LICENSE file for details.