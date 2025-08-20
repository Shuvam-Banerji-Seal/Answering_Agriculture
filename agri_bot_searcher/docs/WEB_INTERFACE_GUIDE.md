# Agriculture Bot Searcher - Web Interface Guide 🌐

## Overview
The Agriculture Bot Searcher Web Interface provides a user-friendly, browser-based interface for interacting with the multi-agent agricultural chatbot system. Built with Flask, it offers comprehensive configuration options and real-time monitoring.

## 🚀 Getting Started

### Quick Launch
```bash
# Start the web interface
./start_web_ui.sh

# Or manually
python src/web_ui.py
```

### Access
Open your browser and navigate to: **http://localhost:5000**

## 🎛️ Interface Components

### 1. Configuration Panel (Left Side)

#### 🔧 System Configuration
- **Ollama Base Port**: Configure the base port for Ollama instances (default: 11434)
- **Number of Agents**: Set how many agents to use (1-6 agents)
- **Web Searches per Query**: Control search intensity (1-5 searches)

#### 🎯 Answer Preferences
- **Detailed Analysis**: Comprehensive responses with context and explanations
- **Concise Answer**: Brief, practical advice in bullet-point format

#### 📊 System Status
- **Real-time monitoring**: Live status of Ollama agent availability
- **Port information**: Shows which ports are active
- **Auto-refresh**: Updates every 30 seconds

### 2. Query Panel (Right Side)

#### 🌱 Query Input
- **Large text area**: Comfortable typing for complex questions
- **Placeholder examples**: Sample queries to guide users
- **Enter to submit**: Press Enter to submit (Ctrl+Enter for new lines)

#### 📈 Results Display
- **Formatted responses**: Proper markdown rendering
- **Performance statistics**: Response time, agents used, citations count
- **Error handling**: Clear error messages and troubleshooting tips

## 🔧 Configuration Options

### System Parameters

| Parameter | Range | Default | Description |
|-----------|--------|---------|-------------|
| **Base Port** | 1024-65535 | 11434 | Starting port for Ollama instances |
| **Agents** | 1-6 | 2 | Number of parallel agents |
| **Searches** | 1-5 | 2 | Web searches per query |

### Answer Modes

#### 📝 Detailed Analysis Mode
- **Use case**: Research, learning, comprehensive understanding
- **Response style**: 300-500 words with context and explanations
- **Citations**: Full source references with links
- **Structure**: Organized sections with headers and bullet points

#### ⚡ Concise Answer Mode
- **Use case**: Quick decisions, practical implementation
- **Response style**: 50-150 words with actionable advice
- **Citations**: Essential sources only
- **Structure**: Direct bullet points and numbered lists

## 🌐 API Endpoints

The web interface provides REST API endpoints for programmatic access:

### Status Endpoint
```http
GET /api/status
```
**Response:**
```json
{
  "available_ports": [11434, 11435],
  "agent_roles": ["crop_specialist", "disease_expert", ...],
  "base_port": 11434,
  "max_agents": 2
}
```

### Query Endpoint
```http
POST /api/query
Content-Type: application/json

{
  "query": "How to treat bacterial blight in rice?",
  "base_port": 11434,
  "num_agents": 2,
  "num_searches": 2,
  "exact_answer": false
}
```

**Response:**
```json
{
  "success": true,
  "answer": "Detailed response with citations...",
  "citations": ["url1", "url2", ...],
  "stats": {
    "execution_time": 25.3,
    "agents_used": 2,
    "citations_count": 5,
    "search_results": 10
  }
}
```

## 💡 Usage Tips

### Best Practices
1. **Start with 2 agents**: Good balance of speed and quality
2. **Use detailed mode for learning**: Better for understanding concepts
3. **Use concise mode for quick decisions**: Faster, actionable advice
4. **Check system status first**: Ensure Ollama is running
5. **Adjust searches based on complexity**: More searches for complex topics

### Sample Queries

#### 🌾 Crop Management
- "Best practices for organic wheat cultivation in semi-arid regions"
- "How to optimize rice yield during monsoon season?"
- "Sustainable corn farming techniques for small-scale farmers"

#### 🐛 Pest & Disease Control
- "Integrated pest management for tomato hornworms"
- "Natural remedies for powdery mildew in cucumbers"
- "Early detection methods for late blight in potatoes"

#### 💧 Irrigation & Water Management
- "Drip irrigation setup for greenhouse vegetables"
- "Water conservation techniques in drought-prone areas"
- "Optimal irrigation scheduling for different crop stages"

#### 🧪 Soil & Nutrition
- "Soil testing and nutrient management for organic gardens"
- "Composting techniques for agricultural waste"
- "Micronutrient deficiency symptoms in citrus trees"

## 🔍 Troubleshooting

### Common Issues

#### ❌ "No agents available"
**Cause**: Ollama not running or wrong port configuration
**Solution**: 
1. Start Ollama: `ollama serve --port 11434`
2. Check port in configuration panel
3. Verify firewall settings

#### ❌ "Connection error"
**Cause**: Network connectivity issues
**Solution**:
1. Check internet connection
2. Verify web search functionality
3. Try different DNS settings

#### ❌ "Server error"
**Cause**: Backend processing issues
**Solution**:
1. Check browser console for errors
2. Refresh the page
3. Restart the web server

### Performance Optimization

#### 🚀 Speed Improvements
- **Reduce agents**: Use 1-2 agents for faster responses
- **Limit searches**: Use 1-2 searches for quicker results
- **Use concise mode**: Shorter processing time

#### 🎯 Quality Improvements
- **Increase agents**: Use 3-4 agents for better coverage
- **More searches**: Use 3-5 searches for comprehensive results
- **Use detailed mode**: More thorough analysis

## 🐳 Docker Deployment

### Using Docker Compose
```bash
# Start with web interface
docker-compose up -d

# Access at http://localhost:5000
```

### Environment Variables
```bash
export HOST=0.0.0.0
export PORT=5000
export DEBUG=false
```

## 🔐 Security Considerations

### Production Deployment
- **Use HTTPS**: Configure SSL/TLS certificates
- **Access control**: Implement authentication if needed
- **Rate limiting**: Add rate limiting for API endpoints
- **Input validation**: Already implemented for query inputs

### Network Security
- **Firewall rules**: Restrict access to necessary ports only
- **VPN access**: Use VPN for remote access in production
- **Regular updates**: Keep dependencies updated

## 📊 Monitoring & Analytics

### Built-in Metrics
- **Response times**: Track query processing speed
- **Agent utilization**: Monitor agent usage patterns
- **Citation quality**: Review source reliability
- **Error rates**: Monitor system health

### Integration Options
- **Logging**: Structured logging for analysis
- **Metrics export**: Prometheus-compatible metrics
- **Health checks**: Built-in health monitoring

## 🛠️ Development

### Local Development
```bash
# Install development dependencies
pip install -r requirements.txt

# Run in debug mode
python src/web_ui.py
```

### Customization
- **Styling**: Modify CSS variables in web_ui.py
- **Features**: Add new endpoints in Flask routes
- **Configuration**: Extend config.yml for new options

---

*For technical support or feature requests, please refer to the main documentation or create an issue in the project repository.*
