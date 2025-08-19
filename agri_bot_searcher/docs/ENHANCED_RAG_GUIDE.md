# Enhanced RAG Integration Guide

This document explains the enhanced RAG (Retrieval-Augmented Generation) system integration in the Agriculture Bot Searcher.

## Overview

The enhanced RAG system combines:
- **Database Retrieval**: Uses pre-computed embeddings from agricultural documents
- **Web Search**: Real-time web search for current information
- **Query Refinement**: Uses Gemma3:1b to improve user queries
- **Sub-query Generation**: Breaks down complex queries into focused sub-queries
- **Multi-source Processing**: Processes each sub-query against both database and web
- **Markdown Report Generation**: Creates comprehensive research reports
- **LLM Synthesis**: Uses Gemma3:27b to synthesize final answers

## Architecture

```
User Query
    ↓
Query Refinement (Gemma3:1b)
    ↓
Sub-query Generation (Gemma3:1b)
    ↓
Parallel Processing:
├── Database Retrieval (FAISS + Embeddings)
└── Web Search (DuckDuckGo)
    ↓
Markdown Report Generation
    ↓
Answer Synthesis (Gemma3:27b)
    ↓
Final Answer + Sources
```

## Features

### 🎯 Query Processing
- **Query Refinement**: Improves crude user queries for better searchability
- **Sub-query Generation**: Creates 1-5 focused sub-queries from the main query
- **Configurable Parameters**: Control number of sub-queries, chunks, and web results

### 📚 Database Retrieval
- **FAISS Vector Search**: Fast similarity search through agricultural embeddings
- **Configurable Chunks**: Retrieve 1-10 database chunks per sub-query
- **Source Metadata**: Includes source information, titles, and similarity scores

### 🌐 Web Search
- **Real-time Search**: DuckDuckGo integration for current information
- **Agricultural Focus**: Automatically adds agriculture-related terms to searches
- **Configurable Results**: Retrieve 1-10 web results per sub-query

### 📄 Markdown Reports
- **Comprehensive Documentation**: All retrieved information organized by sub-query
- **Source Citations**: Proper attribution for both database and web sources
- **Downloadable Reports**: Save complete research reports as markdown files

### 🤖 LLM Synthesis
- **Multiple Model Support**: Choose from available Gemma3 models
- **Context-aware**: Uses full research report for comprehensive answers
- **Fallback Support**: Automatic fallback to smaller models if needed

## Configuration

### Web UI Controls

#### Query Configuration
- **Number of Sub-queries**: 1-5 (default: 3)
  - More sub-queries = more comprehensive coverage
  - Fewer sub-queries = faster processing

#### Database Retrieval
- **Database Chunks per Sub-query**: 1-10 (default: 3)
  - More chunks = more context from database
  - Consider processing time and token limits

#### Web Search
- **Web Results per Sub-query**: 1-10 (default: 3)
  - More results = broader web coverage
  - May include less relevant sources

#### LLM Configuration
- **Synthesis Model**: Choose from available models
  - `gemma3:27b`: Best quality, slower processing
  - `gemma3:8b`: Good balance of quality and speed
  - `gemma3:2b`: Fastest processing, basic quality

### System Requirements

#### Required Models
- `gemma3:1b`: For query refinement and sub-query generation
- `gemma3:27b`: For high-quality answer synthesis (recommended)

#### Required Dependencies
```bash
# Core dependencies
sentence-transformers>=2.2.0
faiss-cpu>=1.7.0
numpy>=1.21.0
duckduckgo-search>=6.0.0

# Web framework
flask>=2.0.0
flask-cors>=4.0.0
```

#### Required Data
- **Embeddings Database**: Must be present in `/store/Answering_Agriculture/agriculture_embeddings/`
  - `faiss_index.bin` or `faiss_index.index`
  - `metadata.json` or `metadata.pkl`
  - `config.json` (optional)

## Usage Examples

### Example 1: Basic Query
**Input**: "How to grow tomatoes?"

**Process**:
1. **Refined Query**: "Best practices for tomato cultivation and growth management"
2. **Sub-queries**:
   - "Tomato soil preparation and planting techniques"
   - "Tomato irrigation and nutrient management"
   - "Tomato pest and disease prevention methods"
3. **Results**: Database chunks + web articles for each sub-query
4. **Final Answer**: Comprehensive tomato growing guide with sources

### Example 2: Complex Agricultural Query
**Input**: "Climate change impact on wheat yield"

**Process**:
1. **Refined Query**: "Climate change effects on wheat production and yield sustainability"
2. **Sub-queries**:
   - "Temperature and precipitation changes affecting wheat growth"
   - "Wheat yield trends under climate change scenarios"
   - "Adaptation strategies for wheat farming in changing climate"
3. **Results**: Research papers + current news articles + policy documents
4. **Final Answer**: Detailed analysis with multiple perspectives and sources

## API Endpoints

### Enhanced RAG Query
```
POST /api/enhanced-query
Content-Type: application/json

{
  "query": "Your agricultural question",
  "num_sub_queries": 3,
  "db_chunks_per_query": 3,
  "web_results_per_query": 3,
  "synthesis_model": "gemma3:27b"
}
```

### System Status
```
GET /api/system-status

Response:
{
  "rag_system_available": true,
  "legacy_chatbot_available": true,
  "embeddings_available": true
}
```

### Available Models
```
GET /api/available-models

Response: ["gemma3:27b", "gemma3:8b", "gemma3:2b", "gemma3:1b"]
```

### Download Report
```
GET /api/download-markdown?file=<path>

Returns: markdown file download
```

## Performance Considerations

### Processing Time
- **Query Refinement**: ~1-2 seconds
- **Sub-query Generation**: ~2-3 seconds
- **Database Retrieval**: ~0.5-1 second per sub-query
- **Web Search**: ~2-3 seconds per sub-query
- **Answer Synthesis**: ~10-30 seconds (depends on model size)

**Total**: 20-60 seconds for typical queries

### Resource Usage
- **Memory**: 2-8GB RAM (depends on embedding model)
- **CPU**: Multi-core recommended for parallel processing
- **Storage**: ~1-5GB for embeddings database
- **Network**: Required for web search and Ollama API

### Optimization Tips
1. **Reduce Sub-queries**: Fewer sub-queries = faster processing
2. **Limit Chunks/Results**: Balance between coverage and speed
3. **Use Smaller Models**: gemma3:8b or gemma3:2b for faster synthesis
4. **Cache Results**: Consider implementing caching for repeated queries

## Troubleshooting

### Common Issues

#### "Enhanced RAG system not available"
- Check if embeddings directory exists: `/store/Answering_Agriculture/agriculture_embeddings/`
- Verify FAISS index and metadata files are present
- Install required dependencies: `sentence-transformers`, `faiss-cpu`

#### "Model not found" errors
- Ensure Ollama is running: `ollama serve`
- Download required models: `ollama pull gemma3:1b gemma3:27b`
- Check model availability: `ollama list`

#### Slow processing
- Reduce number of sub-queries and results per query
- Use smaller synthesis model (gemma3:8b instead of gemma3:27b)
- Check system resources (RAM, CPU)

#### Web search failures
- Check internet connectivity
- Verify `duckduckgo-search` package is installed
- Try reducing web results per query

### Logs and Debugging
- Web UI logs appear in terminal running the application
- Ollama logs: Check `ollama serve` output
- Enable debug mode in configuration for detailed logging

## Future Enhancements

1. **Caching System**: Cache query results to improve response times
2. **Advanced Filtering**: Filter sources by credibility, date, domain
3. **Multi-language Support**: Support for regional languages in agriculture
4. **Custom Embeddings**: Train domain-specific embedding models
5. **Real-time Updates**: Automatic updates to embeddings database
6. **Analytics Dashboard**: Track query patterns and system performance

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review system logs for error messages
3. Verify all dependencies are correctly installed
4. Test with simple queries first before complex ones
