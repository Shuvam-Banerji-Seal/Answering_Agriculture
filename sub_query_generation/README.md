# Sub-Query Generation for RAG Systems

A comprehensive Python package for generating multiple sub-queries from a single query to improve Retrieval-Augmented Generation (RAG) performance. The system supports both Ollama and HuggingFace implementations with configurable parameters.

## Architecture Overview

```
sub_query_generation/
├── __init__.py              # Package initialization
├── base.py                  # Abstract base classes and interfaces
├── ollama_generator.py      # Ollama implementation
├── huggingface_generator.py # HuggingFace implementation
├── factory.py               # Factory pattern for generator creation
├── main.py                  # CLI interface
├── examples.py              # Usage examples
├── config.yaml              # Configuration file
├── requirements.txt         # Dependencies
└── README.md               # This file
```

### Core Components

1. **Base Classes** (`base.py`)
   - `SubQueryGenerator`: Abstract base class defining the interface
   - `SubQueryResult`: Data container for results
   - Common prompt generation and response parsing logic

2. **Implementations**
   - `OllamaSubQueryGenerator`: Uses local Ollama models
   - `HuggingFaceSubQueryGenerator`: Uses HuggingFace transformers

3. **Factory Pattern** (`factory.py`)
   - `SubQueryGeneratorFactory`: Creates appropriate generator based on configuration
   - Handles availability checking and configuration loading

4. **CLI Interface** (`main.py`)
   - Command-line tool for standalone usage
   - Multiple output formats (JSON, text, list)

## Features

- **Dual Implementation Support**: Choose between Ollama (local) or HuggingFace (cloud/local)
- **RAG-Optimized Queries**: Generates queries formatted as complete sentences suitable for document retrieval
- **Configurable Strategy**: 5 different query variation types (synonym, technical, simplified, context, perspective)
- **Flexible Configuration**: YAML-based configuration with sensible defaults
- **Error Handling**: Robust error handling with fallback mechanisms
- **Resource Management**: Proper cleanup for GPU resources
- **Logging**: Comprehensive logging for debugging and monitoring

## Installation

### Basic Installation
```bash
pip install pyyaml requests
```

### For HuggingFace Support
```bash
pip install transformers torch accelerate bitsandbytes
```

### For Development
```bash
pip install -r requirements.txt
```

### Ollama Setup
1. Install Ollama: https://ollama.ai/
2. Pull a model: `ollama pull gemma2:2b`
3. Start Ollama service: `ollama serve`

## Configuration

The system uses a YAML configuration file (`config.yaml`) with the following structure:

```yaml
# Model Configuration
model:
  implementation: 'ollama'  # or 'huggingface'
  
  ollama:
    model_name: 'gemma2:2b'
    base_url: 'http://localhost:11434'
    timeout: 30
  
  huggingface:
    model_id: 'google/gemma-2-2b-it'
    use_quantization: false
    quantization_bits: 8
    device: 'auto'
    torch_dtype: 'bfloat16'

# Generation Parameters
generation:
  temperature: 0.7
  max_new_tokens: 1000
  do_sample: true
  num_sub_queries: 5

# Strategy Configuration
strategy:
  variations:
    - synonym_variation
    - technical_reformulation
    - simplified_version
    - context_expansion
    - perspective_shift
  
  rag_optimization:
    sentence_format: true
    keyword_focus: true
    max_length_per_query: 2

# Logging
logging:
  level: 'INFO'
  file: 'sub_query_generation.log'
```

## Usage

### Python API

```python
from sub_query_generation import SubQueryGeneratorFactory

# Using configuration file
generator = SubQueryGeneratorFactory.create_generator("config.yaml")

# Using configuration dictionary
config = {
    'model': {'implementation': 'ollama'},
    'generation': {'num_sub_queries': 5}
}
generator = SubQueryGeneratorFactory.create_generator(config_dict=config)

# Generate sub-queries
query = "Why is the protein content in rice less than other grains?"
result = generator.generate_sub_queries(query)

print(f"Original: {result.original_query}")
for i, sub_query in enumerate(result.sub_queries, 1):
    print(f"{i}. {sub_query}")
```

### Command Line Interface

```bash
# Basic usage
python -m sub_query_generation.main "Why is protein content in rice low?"

# With custom config
python -m sub_query_generation.main "Your query" --config custom_config.yaml

# Different output formats
python -m sub_query_generation.main "Your query" --format text
python -m sub_query_generation.main "Your query" --format list

# Save to file
python -m sub_query_generation.main "Your query" --output results.json

# Override implementation
python -m sub_query_generation.main "Your query" --implementation huggingface

# Check availability
python -m sub_query_generation.main --check-availability
```

### RAG Integration Example

```python
from sub_query_generation import SubQueryGeneratorFactory

# Initialize generator
generator = SubQueryGeneratorFactory.create_generator("config.yaml")

# Original user query
user_query = "How to improve soil fertility naturally?"

# Generate sub-queries
result = generator.generate_sub_queries(user_query)

# Use all queries for retrieval
all_queries = [user_query] + result.sub_queries

# In your RAG system:
retrieved_docs = []
for query in all_queries:
    # 1. Convert query to embeddings
    query_embedding = embed_query(query)
    
    # 2. Search vector database
    docs = vector_db.search(query_embedding, top_k=5)
    retrieved_docs.extend(docs)

# 3. Remove duplicates and rank
unique_docs = deduplicate_and_rank(retrieved_docs)

# 4. Generate final answer using retrieved docs
answer = llm.generate(user_query, unique_docs)
```

## Query Generation Strategy

The system generates 5 types of query variations:

1. **Synonym Variation**: Replaces key terms with synonyms
   - Original: "Why is protein content in rice low?"
   - Variation: "What factors contribute to reduced protein levels in rice grains?"

2. **Technical Reformulation**: Uses domain-specific terminology
   - Variation: "Rice protein yield and nutritional content analysis"

3. **Simplified Version**: Uses everyday language
   - Variation: "Why doesn't rice have much protein?"

4. **Context Expansion**: Adds implicit context
   - Variation: "Protein deficiency in rice compared to wheat and other cereals"

5. **Perspective Shift**: Different angle or use case
   - Variation: "Nutritional limitations of rice-based diets"

## Performance Considerations

### Ollama
- **Pros**: Local execution, privacy, no API costs
- **Cons**: Requires local setup, GPU memory usage
- **Best for**: Privacy-sensitive applications, offline usage

### HuggingFace
- **Pros**: Wide model selection, quantization support
- **Cons**: Higher memory usage, slower cold start
- **Best for**: Research, experimentation, custom models

### Optimization Tips
1. Use quantization for HuggingFace models to reduce memory usage
2. Cache generators to avoid reloading models
3. Batch multiple queries when possible
4. Use appropriate temperature settings (0.7 recommended)

## Error Handling

The system includes comprehensive error handling:

- **Model Availability**: Checks if models are loaded/accessible
- **Network Issues**: Handles Ollama connection problems
- **Memory Issues**: Graceful handling of GPU memory constraints
- **Parsing Failures**: Fallback to original query if parsing fails
- **Configuration Errors**: Clear error messages for config issues

## Logging

Configurable logging helps with debugging and monitoring:

```python
# Enable debug logging
config['logging']['level'] = 'DEBUG'

# Log to file
config['logging']['file'] = 'sub_query_generation.log'
```

Log levels:
- `DEBUG`: Detailed execution information
- `INFO`: General operational messages
- `WARNING`: Important notices
- `ERROR`: Error conditions

## Testing

Run the examples to test your setup:

```bash
python -m sub_query_generation.examples
```

This will:
1. Check implementation availability
2. Run example queries
3. Demonstrate RAG integration
4. Show different output formats

## Troubleshooting

### Ollama Issues
- **Connection refused**: Ensure Ollama is running (`ollama serve`)
- **Model not found**: Pull the model (`ollama pull gemma2:2b`)
- **Timeout errors**: Increase timeout in config

### HuggingFace Issues
- **CUDA out of memory**: Enable quantization or use CPU
- **Model download fails**: Check internet connection and HF token
- **Import errors**: Install required packages

### General Issues
- **No sub-queries generated**: Check model output and parsing logic
- **Poor quality queries**: Adjust temperature or try different model
- **Slow performance**: Use smaller models or quantization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Changelog

### v1.0.0
- Initial release
- Ollama and HuggingFace implementations
- CLI interface
- Comprehensive configuration system
- RAG-optimized query generation