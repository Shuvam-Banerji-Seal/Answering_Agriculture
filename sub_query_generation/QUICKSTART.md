# Quick Start Guide

Get up and running with sub-query generation in 5 minutes!

## 1. Choose Your Implementation

### Option A: Ollama (Recommended for local use)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull gemma2:2b

# Start Ollama (in background)
ollama serve &
```

### Option B: HuggingFace (More model options)
```bash
# Install dependencies
pip install transformers torch accelerate bitsandbytes
```

## 2. Install Package Dependencies
```bash
pip install pyyaml requests
```

## 3. Test Your Setup
```bash
cd sub_query_generation
python test_system.py
```

## 4. Run Your First Query

### Using Python API
```python
from sub_query_generation import SubQueryGeneratorFactory

# Quick config for Ollama
config = {
    'model': {'implementation': 'ollama'},
    'generation': {'num_sub_queries': 5}
}

generator = SubQueryGeneratorFactory.create_generator(config_dict=config)
result = generator.generate_sub_queries("Why is rice protein content low?")

print("Sub-queries:")
for i, query in enumerate(result.sub_queries, 1):
    print(f"{i}. {query}")
```

### Using CLI
```bash
python -m sub_query_generation.main "Why is rice protein content low?"
```

## 5. Customize Configuration

Edit `config.yaml` to change:
- Model selection
- Number of sub-queries
- Generation parameters
- Output format

## 6. Integrate with Your RAG System

```python
# Your existing RAG code
user_query = "How to improve crop yields?"

# Generate sub-queries
result = generator.generate_sub_queries(user_query)
all_queries = [user_query] + result.sub_queries

# Use all queries for better retrieval
for query in all_queries:
    docs = your_vector_db.search(query)
    # Process documents...
```

## Common Issues

**Ollama connection error**: Make sure Ollama is running (`ollama serve`)

**Model not found**: Pull the model first (`ollama pull gemma2:2b`)

**CUDA out of memory**: Enable quantization in config or use CPU

**No sub-queries generated**: Check model output in debug mode

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [examples.py](examples.py) for more usage patterns
- Customize the prompt in `base.py` for your domain
- Experiment with different models and parameters

Happy querying! 🚀