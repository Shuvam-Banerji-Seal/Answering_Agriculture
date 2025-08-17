"""
API endpoint tests
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"

def test_home_page():
    """Test home page renders"""
    response = client.get("/")
    assert response.status_code == 200
    assert "IndicAgri" in response.text

def test_query_endpoint():
    """Test query processing endpoint"""
    query_data = {
        "query": "धान की फसल में पीले पत्ते क्यों होते हैं?",
        "language": "hi",
        "input_type": "text"
    }
    
    response = client.post("/api/v1/query", json=query_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "answer" in data
    assert "confidence" in data
    assert isinstance(data["sources"], list)

def test_invalid_query():
    """Test handling of invalid queries"""
    response = client.post("/api/v1/query", json={})
    assert response.status_code == 422  # Validation error

if __name__ == "__main__":
    pytest.main([__file__])
            