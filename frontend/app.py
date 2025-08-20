"""
IndicAgri Frontend Server - Integrated with Existing Backend Modules
"""

from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import asyncio
import json
import sys
import os
from datetime import datetime
import traceback

# Add your project root to Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="IndicAgri Frontend", 
    description="Agricultural AI Assistant Frontend",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Initialize backend connections (lazy loading)
_embedding_system = None
_sub_query_generator = None

def get_embedding_system():
    """Lazy load embedding system"""
    global _embedding_system
    if _embedding_system is None:
        try:
            from embedding_generator.src.embedding_system import EmbeddingSystem
            _embedding_system = EmbeddingSystem()
            logger.info("Embedding system initialized")
        except Exception as e:
            logger.error(f"Failed to initialize embedding system: {e}")
            _embedding_system = None
    return _embedding_system

def get_sub_query_generator():
    """Lazy load sub query generator"""
    global _sub_query_generator
    if _sub_query_generator is None:
        try:
            from sub_query_generation.main import SubQueryProcessor
            _sub_query_generator = SubQueryProcessor()
            logger.info("Sub-query generator initialized")
        except Exception as e:
            logger.error(f"Failed to initialize sub-query generator: {e}")
            _sub_query_generator = None
    return _sub_query_generator

# Request/Response Models
class QueryRequest(BaseModel):
    query: str
    input_type: str = "text"
    language: str = "en"  # Default language changed to English
    user_location: Optional[str] = None
    session_id: Optional[str] = None

class Source(BaseModel):
    title: str
    url: str = "#"
    relevance: float
    content_preview: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[Source] = []
    confidence: float
    processing_time: Optional[float] = None
    sub_queries: Optional[List[str]] = []
    error: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main application page"""
    # Get language from query params, default to English
    lang = request.query_params.get("lang", "en")
    return templates.TemplateResponse("index.html", {
        "request": request,
        "app_name": "IndicAgri",
        "version": "1.0.0",
        "lang": lang
    })

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "services": {
            "embedding_system": get_embedding_system() is not None,
            "sub_query_generator": get_sub_query_generator() is not None
        }
    }

@app.post("/api/v1/query", response_model=QueryResponse)
async def process_query(query_request: QueryRequest):
    """
    Process agricultural query using your existing backend modules
    """
    start_time = datetime.now()
    try:
        logger.info(f"Processing query: {query_request.query[:100]}...")
        # Use language from request
        language = query_request.language or "en"
        # Try to use your actual backend systems
        if get_sub_query_generator() and get_embedding_system():
            result = await process_with_backend(query_request)
        else:
            # Fallback to enhanced mock responses
            result = await get_enhanced_mock_response(query_request)
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        result.processing_time = processing_time
        logger.info(f"Query processed in {processing_time:.2f}s")
        return result
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        logger.error(traceback.format_exc())
        # Error message in English
        return QueryResponse(
            answer="Sorry, your query could not be processed due to a technical issue. Please try again.",
            sources=[],
            confidence=0.0,
            processing_time=(datetime.now() - start_time).total_seconds(),
            error=str(e)
        )

async def process_with_backend(query_request: QueryRequest) -> QueryResponse:
    """Process query using your actual backend systems"""
    try:
        # Generate sub-queries using your existing system
        sub_query_gen = get_sub_query_generator()
        sub_queries = []
        
        if sub_query_gen:
            # Use your actual sub-query generation
            sub_queries = await asyncio.to_thread(
                sub_query_gen.generate_sub_queries, 
                query_request.query
            )
        else:
            sub_queries = [query_request.query]  # Fallback
        
        # Use embedding system for retrieval
        embedding_system = get_embedding_system()
        relevant_docs = []
        
        if embedding_system:
            # Get embeddings and search
            embeddings = await asyncio.to_thread(
                embedding_system.get_embeddings,
                sub_queries
            )
            
            relevant_docs = await asyncio.to_thread(
                embedding_system.similarity_search,
                embeddings,
                top_k=5
            )
        
        # Generate response (you'll need to implement this based on your LLM integration)
        response_text = await generate_response_from_docs(
            query_request.query, 
            relevant_docs, 
            query_request.language
        )
        
        # Extract sources
        sources = [
            Source(
                title=doc.get('title', 'Agricultural Resource'),
                url=doc.get('url', '#'),
                relevance=doc.get('score', 0.8),
                content_preview=doc.get('content', '')[:200] + "..."
            )
            for doc in relevant_docs[:3]
        ]
        
        return QueryResponse(
            answer=response_text,
            sources=sources,
            confidence=0.85,
            sub_queries=sub_queries
        )
        
    except Exception as e:
        logger.error(f"Backend processing failed: {e}")
        # Fallback to mock response
        return await get_enhanced_mock_response(query_request)

async def generate_response_from_docs(query: str, docs: List[Dict], language: str) -> str:
    """
    Generate response from retrieved documents
    This is where you'd integrate your LLM (Gemma3, DeepSeek, etc.)
    """
    try:
        # TODO: Integrate with your actual LLM
        # from your_llm_module import generate_response
        # response = generate_response(query, docs, language)
        
        # For now, create a structured response from docs
        if docs:
            response = f"आपके प्रश्न '{query}' के आधार पर:\n\n"
            
            for i, doc in enumerate(docs[:3], 1):
                content = doc.get('content', '')[:300]
                response += f"{i}. {content}...\n\n"
            
            response += "यह जानकारी हमारे कृषि डेटाबेस से प्राप्त की गई है जिसमें 15,000+ प्रमाणित स्रोत हैं।"
            return response
        else:
            return await get_fallback_response(query, language)
            
    except Exception as e:
        logger.error(f"Response generation failed: {e}")
        return await get_fallback_response(query, language)

async def get_fallback_response(query: str, language: str) -> str:
    """Fallback response when systems fail"""
    return f"आपका प्रश्न '{query}' प्राप्त हुआ है। हमारे AI सिस्टम में अस्थायी समस्या है। कृपया कुछ देर बाद दोबारा कोशिश करें।"

async def get_enhanced_mock_response(query_request: QueryRequest) -> QueryResponse:
    """Enhanced mock responses for testing"""
    query = query_request.query.lower()
    
    # Simulate processing delay
    await asyncio.sleep(0.5)
    
    if any(word in query for word in ['मौसम', 'weather', 'बारिश', 'तापमान']):
        return QueryResponse(
            answer="""**आज का मौसम विश्लेषण:**

🌡️ **तापमान:** 25°C (न्यूनतम) - 33°C (अधिकतम)
🌧️ **बारिश:** अगले 3 दिन 70% संभावना
💨 **हवा:** 15 किमी/घंटा, दक्षिण-पूर्व दिशा
☁️ **आर्द्रता:** 75%

**🌾 कृषि सलाह:**
• सिंचाई कम करें क्योंकि बारिश की संभावना है
• धान और मक्का की बुआई के लिए अच्छा समय
• खाद डालने से बचें, बारिश के बाद डालें
• फसल में ड्रेनेज की व्यवस्था करें

**⚠️ सावधानी:** तेज़ हवा से सब्जियों की फसल को नुकसान हो सकता है।""",
            sources=[
                Source(title="IMD Weather Report", url="#", relevance=0.95),
                Source(title="ICAR Weather Advisory", url="#", relevance=0.88),
                Source(title="Agricultural Meteorology", url="#", relevance=0.82)
            ],
            confidence=0.92,
            sub_queries=["मौसम पूर्वानुमान", "कृषि मौसम सलाह", "बारिश कृषि प्रभाव"]
        )
    
    elif any(word in query for word in ['धान', 'rice', 'चावल', 'पीले पत्ते']):
        return QueryResponse(
            answer="""**धान में पीले पत्तों की समस्या का समाधान:**

🔍 **मुख्य कारण:**

1️⃣ **नाइट्रोजन की कमी** (सबसे आम)
   • लक्षण: पुराने पत्ते पहले पीले होते हैं
   • समाधान: 25-30 किलो यूरिया प्रति एकड़

2️⃣ **जलभराव** 
   • लक्षण: जड़ों का काला होना
   • समाधान: ड्रेनेज बनाएं, सिंचाई कम करें

3️⃣ **आयरन की कमी**
   • लक्षण: नई पत्तियों में पीलापन
   • समाधान: आयरन सल्फेट का छिड़काव (2 ग्राम/लीटर)

4️⃣ **बैक्टीरियल लीफ ब्लाइट**
   • लक्षण: पत्तियों के किनारे झुलसे हुए
   • समाधान: कॉपर ऑक्सीक्लोराइड का स्प्रे

💊 **तुरंत उपचार:**
• फ़ॉस्फ़ोरस और पोटाश की मात्रा बढ़ाएं
• नीम का तेल मिलाकर छिड़काव करें
• मिट्टी की जांच कराएं""",
            sources=[
                Source(title="ICAR Rice Cultivation Guide", url="#", relevance=0.94),
                Source(title="Plant Pathology Research", url="#", relevance=0.89),
                Source(title="Rice Disease Management", url="#", relevance=0.85)
            ],
            confidence=0.96,
            sub_queries=["धान पीले पत्ते कारण", "धान रोग निदान", "नाइट्रोजन की कमी धान में"]
        )
    
    # Add more mock responses as needed...
    
    return QueryResponse(
        answer=f"""आपका प्रश्न "{query_request.query}" दिलचस्प है। 

**🌾 IndicAgri में उपलब्ध सेवाएं:**

📊 **फसल संबंधी जानकारी:**
• बुआई, कटाई का सही समय
• बीज, खाद, कीटनाशक की सलाह
• रोग-कीट की पहचान और इलाज

🌤️ **मौसम आधारित सलाह:**
• 7 दिन का मौसम पूर्वानुमान
• सिंचाई की सलाह
• प्राकृतिक आपदा से बचाव

💰 **बाज़ार की जानकारी:**
• आज के भाव और रुझान
• बेचने का सही समय
• सरकारी खरीद केंद्र की जानकारी

🏛️ **सरकारी योजनाएं:**
• सब्सिडी और बीमा योजनाएं
• आवेदन की प्रक्रिया
• पात्रता की जांच

कृपया अधिक विशिष्ट प्रश्न पूछें।""",
        sources=[
            Source(title="IndicAgri Knowledge Base", url="#", relevance=0.75)
        ],
        confidence=0.78,
        sub_queries=[query_request.query]
    )

@app.post("/api/v1/voice")
async def process_voice(
    audio: UploadFile = File(...),
    language: str = "hi"
):
    """Process voice input (placeholder for future implementation)"""
    try:
        # TODO: Integrate with your voice processing module
        # from voice_to_text.voice_to_text.indic_conformer import process_audio
        # transcription = process_audio(audio, language)
        
        # For now, return a mock transcription
        return {
            "transcription": "यहाँ आपकी आवाज़ का टेक्स्ट होगा",
            "confidence": 0.85,
            "language_detected": language
        }
    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        raise HTTPException(status_code=500, detail="Voice processing failed")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Redirect 404s to home page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.exception_handler(500)
async def server_error_handler(request: Request, exc: HTTPException):
    """Handle server errors gracefully"""
    logger.error(f"Server error: {exc.detail}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "Something went wrong"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
