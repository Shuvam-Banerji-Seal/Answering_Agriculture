# Configuration Files

This directory contains configuration files for the Agriculture Embedding Generator.

## Available Configurations

### `default_config.yaml`
The default configuration file with comprehensive settings for all aspects of embedding generation.

### `qwen_config.yaml`
Specific configuration for Qwen3-Embedding-8B model that matches the original setup used to generate the `agriculture_embeddings` directory.

## Configuration Structure

### Model Configuration
- `model.name`: HuggingFace model identifier
- `model.device`: Computing device (auto, cuda, cpu)
- `model.trust_remote_code`: Whether to trust remote code for model loading

### Text Processing
- `text_processing.chunk_size`: Maximum tokens per chunk
- `text_processing.chunk_overlap`: Overlap between chunks
- `text_processing.min_chunk_length`: Minimum characters for valid chunks

### Index Configuration
- `index.type`: FAISS index type (flat, ivf)
- `index.similarity_metric`: Similarity metric (cosine, euclidean)
- `index.normalize_vectors`: Whether to normalize vectors

### Processing Configuration
- `processing.batch_size`: Batch size for processing
- `processing.max_records`: Maximum records to process
- `processing.show_progress`: Show progress bars

### Output Configuration
- `output.*`: Control which files to save

## Usage

### Using Default Configuration
```bash
python src/create_embeddings.py --config config/default_config.yaml --input data.jsonl
```

### Using Qwen Configuration
```bash
python src/create_embeddings.py --config config/qwen_config.yaml --input data.jsonl
```

### Override Specific Settings
```bash
python src/create_embeddings.py --config config/qwen_config.yaml --chunk-size 512 --device cpu
```

## Creating Custom Configurations

Copy one of the existing configuration files and modify the settings as needed:

```bash
cp config/default_config.yaml config/my_config.yaml
# Edit my_config.yaml with your settings
python src/create_embeddings.py --config config/my_config.yaml --input data.jsonl
```

## Configuration Priority

Command line arguments override configuration file settings:

1. Command line arguments (highest priority)
2. Configuration file settings
3. Default values in code (lowest priority)

## Original Configuration

The `qwen_config.yaml` file contains the exact configuration used to generate the original `agriculture_embeddings` directory:

- Model: Qwen/Qwen3-Embedding-8B
- Chunk size: 256 tokens
- Chunk overlap: 25 tokens
- Output dimension: 4096
- Total embeddings generated: 7,037
- Source records: 100