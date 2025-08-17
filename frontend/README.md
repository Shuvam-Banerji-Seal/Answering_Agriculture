# IndicAgri Frontend

Modern, responsive web interface for the IndicAgri agricultural AI assistant.

## 🌟 Features

- **Voice-First Design**: Large, accessible voice input with multi-language support
- **Responsive Interface**: Optimized for mobile, tablet, and desktop
- **Multi-Language Support**: 10+ Indian languages with real-time switching
- **Progressive Web App**: Installable, offline-capable
- **Real-time Chat**: Interactive chat interface with typing animations
- **Accessibility**: Screen reader support, keyboard navigation

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js (optional, for advanced development)

### Installation

```
cd frontend

# Install Python dependencies
pip install -r requirements.txt

# Run the development server
python app.py
```

The application will be available at `http://localhost:8000`

### Development

```
# Run with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## 🏗️ Architecture

```
frontend/
├── static/                 # Static assets
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript modules
│   └── images/            # Images and icons
├── templates/             # HTML templates
├── config/                # Configuration files
└── app.py                 # FastAPI server
```

## 🎨 Customization

### Colors
Edit CSS custom properties in `static/css/main.css`:

```
:root {
    --primary-green: #2E7D2E;
    --primary-green-light: #4CAF50;
    --soil-amber: #FF8F00;
}
```

### Languages
Add new languages in:
1. `config/frontend_config.yaml`
2. HTML language dropdown
3. JavaScript language mapping

### Features
Toggle features in `config/frontend_config.yaml`:

```
features:
  voice_recognition: true
  speech_synthesis: true
  offline_mode: true
```

## 🔧 Backend Integration

The frontend connects to your RAG system through the `/api/v1/query` endpoint.

To integrate with your existing modules:

```
# In app.py
from sub_query_generation.main import process_query
from embedding_generator.src.embedding_system import EmbeddingSystem

# Replace mock response with actual processing
result = await process_query(query_request.query)
```

## 📱 Progressive Web App

The frontend includes PWA capabilities:
- Service worker for offline functionality
- Web app manifest for installation
- Responsive design for all devices

## 🧪 Testing

```
# Test the API endpoints
curl -X POST "http://localhost:8000/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "धान की फसल में पीले पत्ते क्यों?"}'
```

## 🚀 Deployment

### Local Deployment
```
python app.py
```

### Production Deployment
```
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment
```
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🎯 Key Components

### Voice Recognition
- Uses Web Speech API
- Supports 22 Indian languages
- Fallback to text input

### Chat Interface
- Real-time messaging
- Source citations
- Typing animations
