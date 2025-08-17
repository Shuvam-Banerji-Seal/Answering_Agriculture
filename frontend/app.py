"""
IndicAgri Frontend Server
FastAPI server to serve frontend and connect to backend RAG system
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import asyncio
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="IndicAgri Frontend", description="Agricultural AI Assistant Frontend")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Request/Response Models
class QueryRequest(BaseModel):
    query: str
    input_type: str = "text"
    language: str = "hi"
    user_location: Optional[str] = None

class Source(BaseModel):
    title: str
    url: str
    relevance: float

class QueryResponse(BaseModel):
    answer: str
    sources: List[Source] = []
    confidence: float
    processing_time: Optional[float] = None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main application page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/query", response_model=QueryResponse)
async def process_query(query_request: QueryRequest):
    """
    Process agricultural query using the backend RAG system
    
    This endpoint will be connected to your actual RAG pipeline
    from the sub_query_generation and embedding_generator modules
    """
    try:
        logger.info(f"Processing query: {query_request.query[:100]}...")
        
        # TODO: Integrate with your actual RAG system
        # from sub_query_generation.main import process_agricultural_query
        # result = await process_agricultural_query(query_request.query)
        
        # For now, return mock response based on query content
        response = await get_mock_response(query_request)
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_mock_response(query_request: QueryRequest) -> QueryResponse:
    """
    Mock response generator for testing
    Replace this with your actual RAG system integration
    """
    query = query_request.query.lower()
    
    # Simulate processing time
    await asyncio.sleep(1)
    
    if 'मौसम' in query or 'weather' in query:
        return QueryResponse(
            answer="""आज का मौसम साफ है। तापमान 25°C है। अगले 3 दिन बारिश की संभावना है। 
            
कृषि सलाह:
• अपनी फसल को बारिश से बचाने के लिए उचित व्यवस्था करें
• सिंचाई कम करें क्योंकि बारिश होने वाली है
• खाद डालने से बचें, बारिश के बाद डालें""",
            sources=[
                Source(title="IMD Weather Report", url="#", relevance=0.95),
                Source(title="Agricultural Weather Advisory", url="#", relevance=0.88)
            ],
            confidence=0.92,
            processing_time=1.2
        )
    
    elif 'धान' in query or 'rice' in query:
        return QueryResponse(
            answer="""धान की फसल में पीले पत्ते की समस्या के मुख्य कारण:

1. **नाइट्रोजन की कमी**: सबसे आम कारण
   • समाधान: 25-30 किलो यूरिया प्रति एकड़

2. **पानी की अधिकता**: जलभराव के कारण
   • समाधान: सिंचाई में संयम, ड्रेनेज बनाएं

3. **आयरन की कमी**: विशेष रूप से क्षारीय मिट्टी में
   • समाधान: आयरन सल्फेट का छिड़काव

4. **रोग**: बैक्टीरियल लीफ ब्लाइट
   • समाधान: कॉपर-आधारित दवा का प्रयोग""",
            sources=[
                Source(title="ICAR Rice Cultivation Guide", url="#", relevance=0.94),
                Source(title="Plant Pathology Research", url="#", relevance=0.87)
            ],
            confidence=0.96,
            processing_time=1.5
        )
    
    elif 'कीमत' in query or 'price' in query:
        return QueryResponse(
            answer="""**आज के मंडी भाव (₹ प्रति क्विंटल):**

📈 **अनाज:**
• गेहूं: ₹2,150 (↑₹50)
• धान: ₹1,980 (↑₹30)
• मक्का: ₹1,850 (↓₹20)

🌱 **दालें:**
• चना: ₹5,200 (↑₹100)
• मूंग: ₹7,500 (↑₹200)
• अरहर: ₹6,800 (↑₹150)

🥬 **सब्जियां:**
• प्याज: ₹3,500 (↑₹300)
• आलू: ₹1,200 (↓₹100)
• टमाटर: ₹4,000 (↑₹500)

**बाजार पूर्वानुमान:** अगले सप्ताह दालों की कीमतों में और वृद्धि की संभावना है।""",
            sources=[
                Source(title="APMC Market Prices", url="#", relevance=0.98),
                Source(title="Agricultural Market Intelligence", url="#", relevance=0.91)
            ],
            confidence=0.95,
            processing_time=0.8
        )
    
    elif 'योजना' in query or 'scheme' in query:
        return QueryResponse(
            answer="""**प्रमुख कृषि योजनाएं 2025:**

🎯 **PM-KISAN:**
• ₹6,000 प्रति वर्ष (₹2,000 की 3 किस्तें)
• सभी भूमिधारक किसान पात्र
• ऑनलाइन आवेदन: pmkisan.gov.in

🌱 **PM फसल बीमा योजना:**
• प्राकृतिक आपदा से सुरक्षा
• खरीफ: 2% प्रीमियम, रबी: 1.5%
• 72 घंटे में नुकसान की रिपोर्ट करें

💧 **प्रधानमंत्री कृषि सिंचाई योजना:**
• ड्रिप और स्प्रिंकलर सिस्टम पर 55% सब्सिडी
• SC/ST किसानों के लिए 75% सब्सिडी

🚜 **कृषि यंत्रीकरण:**
• ट्रैक्टर खरीदने पर 25-50% सब्सिडी
• कस्टम हायरिंग सेंटर स्थापना""",
            sources=[
                Source(title="Ministry of Agriculture & Farmers Welfare", url="#", relevance=0.97),
                Source(title="PM-KISAN Official Portal", url="#", relevance=0.93)
            ],
            confidence=0.94,
            processing_time=1.1
        )
    
    else:
        return QueryResponse(
            answer=f"""आपका प्रश्न "{query_request.query}" बहुत दिलचस्प है। 

हमारी AI प्रणाली निम्नलिखित विषयों पर विशेष जानकारी प्रदान कर सकती है:

🌾 **फसल संबंधी:** रोग, कीट, खाद, बुआई
📊 **बाजार की जानकारी:** कीमतें, मांग, भंडारण
🌤️ **मौसम सलाह:** पूर्वानुमान, कृषि सलाह  
🏛️ **सरकारी योजनाएं:** सब्सिडी, बीमा, लोन
🚜 **कृषि तकनीक:** यंत्र, नई विधियां

कृपया अधिक विशिष्ट प्रश्न पूछें ताकि मैं आपको बेहतर सहायता प्रदान कर सकूं।""",
            sources=[
                Source(title="IndicAgri Knowledge Base", url="#", relevance=0.75)
            ],
            confidence=0.78,
            processing_time=0.5
        )

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("index.html", {"request": request})

@app.exception_handler(500)
async def server_error_handler(request: Request, exc: HTTPException):
    logger.error(f"Server error: {exc.detail}")
    return {"error": "Internal server error", "detail": str(exc.detail)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
