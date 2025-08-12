# API Reference

## AgricultureEmbeddingSystem

The main class for generating embeddings from agricultural text data.

### Constructor

```python
AgricultureEmbeddingSystem(
    model_name: str = "Qwen/Qwen3-Embedding-8B",
    chunk_size: int = 256,
    chunk_overlap: int = 25,
    device: str = "auto"
)
```

**Parameters:**
- `model_name`: HuggingFace model identifier
- `chunk_size`: Maximum tokens per text chunk
- `chunk_overlap`: Number of overlapping tokens between chunks
- `device`: Computing device ("auto", "cuda", "cpu")

### Methods

#### `chunk_text(text: str) -> List[Tuple[str, int, int]]`

Split text into overlapping chunks.

**Parameters:**
- `text`: Input text to chunk

**Returns:**
- List of tuples containing (chunk_text, start_position, end_position)

**Example:**
```python
chunks = system.chunk_text("Long agricultural text...")
for chunk_text, start, end in chunks:
    print(f"Chunk: {chunk_text[:50]}...")
```

#### `create_embedding(text: str) -> np.ndarray`

Generate embedding vector for text.

**Parameters:**
- `text`: Input text

**Returns:**
- NumPy array containing the embedding vector

**Example:**
```python
embedding = system.create_embedding("Rice farming techniques")
print(f"Embedding shape: {embedding.shape}")
```

#### `process_record(record: Dict[str, Any], record_idx: int) -> List[ChunkMetadata]`

Process a single JSONL record into chunks with embeddings.

**Parameters:**
- `record`: Dictionary containing record data
- `record_idx`: Index of the record

**Returns:**
- List of ChunkMetadata objects

**Example:**
```python
record = {
    "title": "Rice Farming",
    "text_extracted": "Content about rice...",
    "crop_types": ["rice"]
}
chunks = system.process_record(record, 0)
```

#### `process_dataset(jsonl_file: str, max_records: Optional[int] = None, filter_function: Optional[Callable] = None)`

Process entire JSONL dataset.

**Parameters:**
- `jsonl_file`: Path to JSONL file
- `max_records`: Maximum records to process (optional)
- `filter_function`: Function to filter records (optional)

**Returns:**
- Tuple of (processed_records, total_chunks)

**Example:**
```python
# Process all records
processed, chunks = system.process_dataset("data.jsonl")

# Process with limit
processed, chunks = system.process_dataset("data.jsonl", max_records=1000)

# Process with filter
def rice_filter(record):
    return "rice" in record.get("crop_types", [])

processed, chunks = system.process_dataset("data.jsonl", filter_function=rice_filter)
```

#### `build_faiss_index(index_type: str = "flat")`

Build FAISS index for similarity search.

**Parameters:**
- `index_type`: Type of index ("flat" for exact search, "ivf" for approximate)

**Example:**
```python
system.build_faiss_index("flat")  # Exact search
system.build_faiss_index("ivf")   # Faster approximate search
```

#### `save_embeddings(output_dir: str = "embeddings_output")`

Save all embeddings and metadata to disk.

**Parameters:**
- `output_dir`: Directory to save outputs

**Example:**
```python
system.save_embeddings("my_embeddings")
```

### Properties

#### `embeddings: List[np.ndarray]`
List of generated embedding vectors.

#### `metadata: List[ChunkMetadata]`
List of metadata for each chunk.

#### `index: faiss.Index`
FAISS index for similarity search (after calling `build_faiss_index()`).

#### `preprocess_function: Optional[Callable[[str], str]]`
Optional custom preprocessing function for text.

**Example:**
```python
def custom_preprocess(text):
    return text.lower().strip()

system.preprocess_function = custom_preprocess
```

## ChunkMetadata

Dataclass containing metadata for each text chunk.

### Fields

- `record_id: str` - Unique identifier for the source record
- `chunk_id: int` - Index of chunk within the record
- `title: str` - Title of the source document
- `author: str` - Author of the source document
- `link: str` - URL of the source document
- `source_domain: str` - Domain of the source
- `publication_year: str` - Year of publication
- `indian_regions: List[str]` - Relevant Indian regions
- `crop_types: List[str]` - Types of crops mentioned
- `farming_methods: List[str]` - Farming methods mentioned
- `soil_types: List[str]` - Types of soil mentioned
- `climate_info: List[str]` - Climate information
- `fertilizers: List[str]` - Fertilizers mentioned
- `plant_species: List[str]` - Plant species mentioned
- `tags: List[str]` - General tags
- `chunk_text: str` - The actual text content
- `chunk_start: int` - Start position in original text
- `chunk_end: int` - End position in original text
- `content_length: int` - Length of chunk text
- `relevance_score: float` - Relevance score (0.0 to 1.0)

## Utility Functions

### Loading Saved Embeddings

```python
import numpy as np
import pickle
import faiss
import json

# Load embeddings
embeddings = np.load("embeddings_output/embeddings.npy")

# Load metadata
with open("embeddings_output/metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

# Load FAISS index
index = faiss.read_index("embeddings_output/faiss_index.bin")

# Load configuration
with open("embeddings_output/config.json", "r") as f:
    config = json.load(f)
```

### Similarity Search

```python
import faiss

# Load index and metadata
index = faiss.read_index("embeddings_output/faiss_index.bin")
with open("embeddings_output/metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

# Create query embedding
system = AgricultureEmbeddingSystem()
query_embedding = system.create_embedding("rice farming techniques")

# Normalize for cosine similarity
query_embedding = query_embedding.reshape(1, -1)
faiss.normalize_L2(query_embedding)

# Search
distances, indices = index.search(query_embedding, k=5)

# Display results
for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
    chunk = metadata[idx]
    print(f"{i+1}. Similarity: {dist:.3f}")
    print(f"   Title: {chunk.title}")
    print(f"   Text: {chunk.chunk_text[:100]}...")
```

## Error Handling

The system includes robust error handling:

- **Model Loading Errors**: Raises exception if model cannot be loaded
- **File Not Found**: Raises `FileNotFoundError` for missing input files
- **JSON Parsing Errors**: Logs warnings and continues processing
- **Embedding Errors**: Returns zero vector as fallback
- **Memory Errors**: Provides guidance on reducing chunk size or batch size

## Performance Optimization

### GPU Usage
```python
# Force GPU usage
system = AgricultureEmbeddingSystem(device="cuda")

# Check if GPU is being used
import torch
print(f"Using GPU: {torch.cuda.is_available()}")
```

### Memory Management
```python
# Reduce memory usage
system = AgricultureEmbeddingSystem(
    chunk_size=128,  # Smaller chunks
    chunk_overlap=10  # Less overlap
)

# Process in batches
for batch_start in range(0, total_records, batch_size):
    system.process_dataset(file, max_records=batch_size)
    system.save_embeddings(f"batch_{batch_start}")
    system.embeddings.clear()  # Free memory
    system.metadata.clear()
```

### Index Optimization
```python
# For large datasets, use IVF index
system.build_faiss_index("ivf")  # Faster search, slight accuracy trade-off

# For exact search
system.build_faiss_index("flat")  # Slower but exact results
```