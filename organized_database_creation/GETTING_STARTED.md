# Getting Started with Agriculture Database Creation System

## 🚀 Quick Start Guide

This guide will help you get started with the Indian Agriculture Database Creation System using either the keyword-based or autonomous agent approach.

## 📁 Repository Structure Overview

```
organized_database_creation/
├── README.md                           # Main project overview
├── GETTING_STARTED.md                  # This file
├── docs/                              # Comprehensive documentation
│   ├── keyword_approach_diagram.md    # Keyword approach workflow
│   ├── autonomous_approach_diagram.md # Autonomous approach workflow
│   ├── data_format_specification.md   # Output data format details
│   └── comparison_analysis.md         # Detailed approach comparison
├── keyword_based_search/              # Keyword-based approach
│   ├── README.md                      # Approach-specific documentation
│   ├── src/                          # Source code
│   ├── config/                       # Configuration files
│   ├── tests/                        # Test files and examples
│   └── requirements.txt              # Dependencies
├── autonomous_agent_search/           # Autonomous approach
│   ├── README.md                     # Approach-specific documentation
│   ├── src/                         # Source code
│   ├── config/                      # Configuration files
│   ├── tests/                       # Test files and examples
│   └── requirements.txt             # Dependencies
├── shared/                          # Shared utilities
│   ├── jsonl_writer.py             # JSONL output handling
│   └── data_validator.py           # Data validation utilities
├── sample_outputs/                  # Sample dataset outputs
├── setup/                          # Setup and installation
│   ├── install_dependencies.sh     # Automated installation
│   ├── setup.py                   # Setup script
│   └── system_requirements.md     # System requirements
```

## 🛠️ Installation

### Step 1: System Requirements Check

Ensure you have:
- **Python 3.9+**
- **8GB+ RAM** (16GB+ recommended for autonomous approach)
- **Stable internet connection**
- **20GB+ free disk space**

### Step 2: Install Dependencies

```bash
# Navigate to the project directory
cd organized_database_creation

# Run the automated installation script
chmod +x setup/install_dependencies.sh
./setup/install_dependencies.sh

# Or install manually
pip install -r keyword_based_search/requirements.txt
pip install -r autonomous_agent_search/requirements.txt
```

### Step 3: Verify Installation

```bash
# Test keyword-based approach
cd keyword_based_search
python tests/test_installation.py

# Test autonomous approach
cd ../autonomous_agent_search
python tests/test_autonomous.py
```

## 🎯 Choose Your Approach

### Option 1: Keyword-Based Search Approach

**Best for**: Targeted research, limited resources, quick prototyping

**Characteristics**:
- 500-2,000 entries
- 2-6 hours processing time
- Systematic coverage
- Predictable results

**Quick Start**:
```bash
cd keyword_based_search

# Run with default settings
python src/agriculture_data_curator.py

# Run with custom configuration
python src/agriculture_data_curator.py --config config/config.yaml --agents 4

# Test with limited queries
python src/agriculture_data_curator.py --max-queries 20
```

### Option 2: Autonomous Agent Search Approach

**Best for**: Comprehensive datasets, exploratory research, large-scale systems

**Characteristics**:
- 5,000-15,000+ entries
- 4-12 hours processing time
- Comprehensive coverage
- Adaptive learning

**Quick Start**:
```bash
cd autonomous_agent_search

# Run full system (12 agents)
python src/autonomous_agriculture_curator.py

# Test with limited agents
python tests/test_autonomous.py

# Run with custom configuration
python src/autonomous_agriculture_curator.py --config config/autonomous_config.yaml
```

## ⚙️ Configuration

### Keyword-Based Configuration

Edit `keyword_based_search/config/config.yaml`:

```yaml
curator:
  num_agents: 4                    # Number of parallel agents
  max_search_results: 15           # Results per search query
  output_file: "agriculture_data.jsonl"
  max_queries: null                # null for all, number for testing
  min_relevance_score: 0.05        # Quality threshold
```

### Autonomous Agent Configuration

Edit `autonomous_agent_search/config/autonomous_config.yaml`:

```yaml
autonomous_curator:
  num_agents: 12                   # Number of autonomous agents
  searches_per_agent: 75           # Searches per agent
  max_search_results: 30           # Results per search
  max_concurrent_agents: 6         # Concurrent processing limit
  enable_autonomous_generation: true
  progressive_search: true         # Enable learning
```

## 📊 Understanding the Output

Both approaches generate JSONL files with structured agriculture data:

```json
{
  "title": "Smart farming: Leveraging IoT for tomato cultivation",
  "author": "Dr. Singh et al.",
  "link": "https://example.com/research-paper",
  "text_extracted": "Full extracted content...",
  "abstract": "Brief summary...",
  "genre": "article",
  "tags": ["IoT", "tomato", "smart farming"],
  "indian_regions": ["Punjab", "Maharashtra"],
  "crop_types": ["tomato"],
  "farming_methods": ["precision agriculture"],
  "relevance_score": 0.85,
  "content_length": 3245,
  "extraction_timestamp": "2025-08-09T10:30:45"
}
```

## 📈 Monitoring Progress

### Real-time Monitoring

Both systems provide real-time progress updates:

```
🤖 Agent 1: Processing query 15/50 - 23 entries collected
🤖 Agent 2: Processing query 12/50 - 31 entries collected
📊 Total: 156 entries, 98 unique URLs, 45 domains
⏱️ Elapsed: 1h 23m, Estimated remaining: 2h 15m
```

### Log Files

- **Keyword-based**: `agriculture_curator.log`
- **Autonomous**: `autonomous_agriculture_curator.log`

## 🔍 Quality Assessment

### Built-in Quality Metrics

- **Relevance Score**: 0.0-1.0 (agriculture content relevance)
- **Content Length**: Character count validation
- **Source Credibility**: Domain authority scoring
- **Duplicate Detection**: Content and URL deduplication

### Using the Data Validator

```python
from shared.data_validator import AgricultureDataValidator

validator = AgricultureDataValidator()
is_valid, errors = validator.validate_entry(entry)
```

## 🚨 Troubleshooting

### Common Issues

1. **Memory Issues**
   ```bash
   # Reduce concurrent agents
   python src/agriculture_data_curator.py --agents 2
   ```

2. **Network Timeouts**
   ```bash
   # Increase timeout in config
   search_timeout: 30
   ```

3. **Permission Errors**
   ```bash
   chmod +x src/*.py
   ```

4. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Getting Help

- Check `docs/` directory for detailed documentation
- Review `tests/` directory for examples
- Check log files for error details
- Ensure system requirements are met

## 📚 Next Steps

### For Beginners

1. **Start with keyword-based approach** for simplicity
2. **Run test examples** to understand the system
3. **Review sample outputs** to understand data format
4. **Gradually increase scale** as you become comfortable

### For Advanced Users

1. **Use autonomous approach** for comprehensive datasets
2. **Customize agent specializations** for specific domains
3. **Integrate with RAG systems** using the structured output
4. **Contribute improvements** to the codebase

### Integration with RAG Systems

```python
import json

# Load agriculture data for RAG
def load_for_rag(jsonl_file, min_relevance=0.3):
    entries = []
    with open(jsonl_file, 'r') as f:
        for line in f:
            entry = json.loads(line)
            if entry['relevance_score'] >= min_relevance:
                entries.append({
                    'text': entry['text_extracted'],
                    'metadata': {
                        'title': entry['title'],
                        'crops': entry['crop_types'],
                        'regions': entry['indian_regions']
                    }
                })
    return entries
```

## 🎯 Success Metrics

### Expected Results

**Keyword-Based Approach**:
- 500-2,000 structured entries
- 70-85% success rate
- 0.6+ average relevance score
- 60+ unique domains

**Autonomous Agent Approach**:
- 5,000-15,000+ structured entries
- 60-80% success rate
- 0.5+ average relevance score
- 100+ unique domains

### Quality Indicators

- **High relevance entries** (0.7+): 25-40%
- **Government sources**: 20-30%
- **Academic sources**: 25-35%
- **Unique content**: 95%+ after deduplication

## 🤝 Contributing

We welcome contributions! Areas for improvement:

- **New search strategies**
- **Enhanced content extraction**
- **Additional data validation**
- **Performance optimizations**
- **Documentation improvements**

---

**Ready to start collecting comprehensive Indian agriculture data!** 🌾

Choose your approach, follow the installation steps, and begin creating valuable datasets for agricultural research and RAG systems.