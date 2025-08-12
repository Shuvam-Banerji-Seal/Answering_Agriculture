# Keyword-Based Search Approach

## 🎯 Overview

The keyword-based search approach uses a systematic methodology with predefined search queries to collect Indian agriculture data. This approach ensures comprehensive coverage of known agriculture domains through structured search patterns and specialized agent roles.

## 🏗️ Architecture

This approach employs multiple parallel agents, each with specialized roles, processing predefined search queries to systematically collect agriculture data from across the internet.

### Key Components

1. **Agriculture Data Curator** - Main orchestrator managing the entire process
2. **Specialized Agents** - Parallel processing agents with domain expertise
3. **Enhanced Web Search** - Intelligent web scraping with content extraction
4. **PDF Processor** - Advanced PDF text extraction and OCR capabilities
5. **Data Validator** - Quality assurance and relevance scoring
6. **JSONL Writer** - Structured data output management

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- 8GB+ RAM recommended
- Stable internet connection

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run setup (optional)
python tests/test_installation.py
```

### Basic Usage

```bash
# Run with default configuration
python src/agriculture_data_curator.py

# Run with custom configuration
python src/agriculture_data_curator.py --config config/custom_config.yaml

# Test with limited queries
python tests/examples.py
```

## ⚙️ Configuration

Edit `config/config.yaml` to customize:

```yaml
curator:
  num_agents: 4                    # Number of parallel agents
  max_search_results: 15           # Results per search query
  output_file: "agriculture_data.jsonl"
  max_queries: null                # null for all, number for testing
  min_relevance_score: 0.05        # Quality threshold
```

## 📊 Expected Output

- **Data Volume**: 500-2,000 structured entries
- **Processing Time**: 2-6 hours
- **Coverage**: Systematic coverage of predefined categories
- **Quality**: High relevance due to targeted searches

## 🎯 Agent Specializations

- **Agent 0**: Crop production and statistics
- **Agent 1**: Sustainable farming practices
- **Agent 2**: Agricultural policy and economics
- **Agent 3**: Agricultural technology and innovation

## 📋 Search Categories

### Crops
Rice, wheat, cotton, sugarcane, pulses, millets, spices, fruits, vegetables

### Regions
All 28 Indian states and major agricultural zones

### Methods
Organic farming, precision agriculture, irrigation, soil management

### Economics
Agricultural policies, subsidies, market dynamics, farmer welfare

## 🔧 Customization

### Adding New Search Queries

Edit `config/search_queries.py`:

```python
CUSTOM_QUERIES = [
    "your custom agriculture search query",
    "another specific search pattern"
]
```

### Modifying Agent Behavior

Adjust agent specializations in `src/agriculture_data_curator.py`:

```python
AGENT_SPECIALIZATIONS = {
    0: "your custom specialization",
    1: "another specialization"
}
```

## 📈 Performance Optimization

- **Optimal agent count**: 4-8 for most systems
- **Memory usage**: 4-8 GB typical
- **Processing rate**: 100-300 entries/hour
- **Success rate**: 70-85% typical

## 🎯 Use Cases

- Targeted research for specific crops or regions
- Quick prototyping and proof of concept
- Resource-constrained environments
- Domain-specific data collection
- Predictable data requirements

This approach provides systematic, reliable data collection with predictable coverage and quality characteristics.