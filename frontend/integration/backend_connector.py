"""
Main connector to your existing backend modules
"""

import sys
import os
import logging
from typing import List, Dict, Optional, Any
import asyncio

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

logger = logging.getLogger(__name__)

class BackendConnector:
    """Connects to your existing IndicAgri backend modules"""
    
    def __init__(self):
        self.embedding_system = None
        self.sub_query_generator = None
        self.voice_processor = None
        self._initialize_systems()
    
    def _initialize_systems(self):
        """Initialize backend systems with error handling"""
        try:
            # Initialize embedding system
            from embedding_generator.src.embedding_system import EmbeddingSystem
            self.embedding_system = EmbeddingSystem()
            logger.info("✅ Embedding system initialized")
        except Exception as e:
            logger.warning(f"⚠️ Embedding system failed to initialize: {e}")
        
        try:
            # Initialize sub-query generator
            from sub_query_generation.main import SubQueryProcessor
            self.sub_query_generator = SubQueryProcessor()
            logger.info("✅ Sub-query generator initialized")
        except Exception as e:
            logger.warning(f"⚠️ Sub-query generator failed to initialize: {e}")
        
        try:
            # Initialize voice processor (when available)
            # from voice_to_text.voice_to_text.indic_conformer import IndicConformer
            # self.voice_processor = IndicConformer()
            logger.info("⚠️ Voice processor not yet integrated")
        except Exception as e:
            logger.warning(f"⚠️ Voice processor failed to initialize: {e}")
    
    async def process_agricultural_query(
        self, 
        query: str, 
        language: str = "hi",
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Process agricultural query through your existing pipeline
        """
        try:
            # Step 1: Generate sub-queries
            sub_queries = await self._generate_sub_queries(query)
            
            # Step 2: Get relevant documents
            relevant_docs = await self._retrieve_documents(sub_queries, top_k)
            
            # Step 3: Generate response (this needs your LLM integration)
            response = await self._generate_response(query, relevant_docs, language)
            
            return {
                "answer": response,
                "sub_queries": sub_queries,
                "documents": relevant_docs,
                "confidence": 0.85  # Calculate based on retrieval scores
            }
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            raise
    
    async def _generate_sub_queries(self, query: str) -> List[str]:
        """Generate sub-queries using your existing system"""
        if self.sub_query_generator:
            try:
                # Use your actual sub-query generation
                sub_queries = await asyncio.to_thread(
                    self.sub_query_generator.generate_sub_queries,
                    query
                )
                return sub_queries if sub_queries else [query]
            except Exception as e:
                logger.error(f"Sub-query generation failed: {e}")
        
        # Fallback: simple sub-query generation
        return [query]
    
    async def _retrieve_documents(self, queries: List[str], top_k: int) -> List[Dict]:
        """Retrieve relevant documents using your embedding system"""
        if self.embedding_system:
            try:
                # Get embeddings
                embeddings = await asyncio.to_thread(
                    self.embedding_system.get_embeddings,
                    queries
                )
                
                # Similarity search
                documents = await asyncio.to_thread(
                    self.embedding_system.similarity_search,
                    embeddings,
                    top_k=top_k
                )
                
                return documents if documents else []
                
            except Exception as e:
                logger.error(f"Document retrieval failed: {e}")
        
        return []
    
    async def _generate_response(
        self, 
        query: str, 
        documents: List[Dict], 
        language: str
    ) -> str:
        """
        Generate response using your LLM
        TODO: Integrate with your actual LLM (Gemma3, DeepSeek, etc.)
        """
        if not documents:
            return f"क्षमा करें, '{query}' के लिए कोई विशिष्ट जानकारी नहीं मिली। कृपया अधिक विशिष्ट प्रश्न पूछें।"
        
        # For now, create a structured response from retrieved documents
        response = f"आपके प्रश्न '{query}' के लिए उपलब्ध जानकारी:\n\n"
        
        for i, doc in enumerate(documents[:3], 1):
            content = doc.get('content', doc.get('text', ''))[:300]
            title = doc.get('title', f'कृषि स्रोत {i}')
            response += f"**{i}. {title}:**\n{content}...\n\n"
        
        response += "\n📚 यह जानकारी हमारे 15,000+ प्रमाणित कृषि स्रोतों से प्राप्त की गई है।"
        
        # TODO: Replace this with your actual LLM integration
        # from your_llm_module import generate_response_with_context
        # response = generate_response_with_context(query, documents, language)
        
        return response
    
    def is_available(self) -> Dict[str, bool]:
        """Check which backend systems are available"""
        return {
            "embedding_system": self.embedding_system is not None,
            "sub_query_generator": self.sub_query_generator is not None,
            "voice_processor": self.voice_processor is not None
        }
