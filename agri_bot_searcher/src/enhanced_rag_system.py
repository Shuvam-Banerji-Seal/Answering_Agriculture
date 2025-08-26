#!/usr/bin/env python3
"""
Enhanced RAG System with Web Search Integration
Combines embeddings-based retrieval with web search for comprehensive answers
"""

import os
import json
import numpy as np
import faiss
import pickle
import requests
import logging
import asyncio
import tempfile
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Data classes for metadata compatibility
@dataclass
class ChunkMetadata:
    """Metadata for document chunks (needed for pickle compatibility)"""
    source: str = ""
    chunk_id: str = ""
    title: str = ""
    content: str = ""
    url: str = ""
    text: str = ""  # Legacy field
    
    def __post_init__(self):
        # Handle legacy formats
        if hasattr(self, 'text') and self.text and not self.content:
            self.content = self.text

# Import sentence transformers
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

# Import DuckDuckGo search
try:
    from ddgs import DDGS
    HAS_DDGS = True
except ImportError:
    try:
        from duckduckgo_search import DDGS
        HAS_DDGS = True
    except ImportError:
        HAS_DDGS = False


@dataclass
class SearchResult:
    """Web search result with metadata"""
    title: str
    url: str
    snippet: str
    content: Optional[str] = None
    source_type: str = "web"
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    relevance_score: float = 0.0


@dataclass
class DatabaseChunk:
    """Database chunk result with metadata"""
    chunk_text: str
    source: str
    title: str = ""
    chunk_id: str = ""
    source_domain: str = ""
    similarity_score: float = 0.0
    source_type: str = "database"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SubQueryResult:
    """Result from sub-query processing"""
    original_query: str
    sub_queries: List[str]
    web_results: List[SearchResult] = field(default_factory=list)
    db_results: List[DatabaseChunk] = field(default_factory=list)
    markdown_content: str = ""
    agent_info: Dict[str, Any] = field(default_factory=dict)


class QueryRefiner:
    """Refines user queries using Gemma3:1b model"""
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
        self.model = "gemma3:1b"
        self.logger = logging.getLogger(__name__)
    
    def refine_query(self, query: str) -> str:
        """Refine a crude user query to be more specific and searchable"""
        
        prompt = f"""You are an expert agricultural query refiner. Your task is to take a user's crude query about agriculture and refine it to be more specific, clear, and searchable.

Guidelines:
1. Make the query more specific and technical when appropriate
2. Add relevant agricultural context if missing
3. Fix grammar and spelling if needed
4. Keep the core intent of the original query
5. Make it suitable for both database search and web search
6. Return only the refined query, nothing else

Original query: {query}

Refined query:"""

        try:
            response = requests.post(
                f'{self.ollama_host}/api/generate',
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.1,
                        'top_p': 0.9,
                        'num_ctx': 2048
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                refined = response.json()['response'].strip()
                self.logger.info(f"Query refined: '{query}' -> '{refined}'")
                return refined
            else:
                self.logger.warning(f"Query refinement failed, using original: {query}")
                return query
                
        except Exception as e:
            self.logger.error(f"Error refining query: {e}")
            return query


class SubQueryGenerator:
    """Generates sub-queries using Gemma3:1b model"""
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
        self.model = "gemma3:1b"
        self.logger = logging.getLogger(__name__)
    
    def generate_sub_queries(self, query: str, num_queries: int = 3) -> List[str]:
        """Generate multiple sub-queries for comprehensive search"""
        
        prompt = f"""You are an expert at breaking down agricultural queries into specific sub-queries for research.

Given the main query, generate {num_queries} specific sub-queries that cover different aspects of the topic. Each sub-query should be:
1. Specific and focused on one aspect
2. Suitable for database and web search
3. Relevant to agriculture
4. Different from each other

Main query: {query}

Generate exactly {num_queries} sub-queries, one per line, numbered 1-{num_queries}:"""

        try:
            response = requests.post(
                f'{self.ollama_host}/api/generate',
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.3,
                        'top_p': 0.9,
                        'num_ctx': 2048
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                response_text = response.json()['response'].strip()
                
                # Parse sub-queries from numbered list
                sub_queries = []
                lines = response_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('•') or line.startswith('-')):
                        # Remove numbering/bullets and clean up
                        clean_query = line.split('.', 1)[-1].strip() if '.' in line else line
                        clean_query = clean_query.lstrip('•-').strip()
                        if clean_query and len(clean_query) > 10:
                            sub_queries.append(clean_query)
                
                if not sub_queries:
                    # Fallback: split by lines and take non-empty ones
                    sub_queries = [line.strip() for line in lines if line.strip() and len(line.strip()) > 10]
                
                # Ensure we have at least the original query
                if not sub_queries:
                    sub_queries = [query]
                
                # Limit to requested number
                sub_queries = sub_queries[:num_queries]
                
                self.logger.info(f"Generated {len(sub_queries)} sub-queries for: {query}")
                return sub_queries
                
            else:
                self.logger.warning(f"Sub-query generation failed, using original: {query}")
                return [query]
                
        except Exception as e:
            self.logger.error(f"Error generating sub-queries: {e}")
            return [query]


class DatabaseRetriever:
    """Retrieves chunks from the embeddings database"""
    
    def __init__(self, embeddings_dir: str, model_name: str = "all-MiniLM-L6-v2"):
        self.embeddings_dir = embeddings_dir
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)
        
        if not HAS_SENTENCE_TRANSFORMERS:
            raise ImportError("sentence-transformers is required for database retrieval")
        
        # Determine device (GPU if available) with memory check
        import torch
        self.device = 'cuda' if torch.cuda.is_available() and self._check_gpu_memory() else 'cpu'
        self.logger.info(f"Using device: {self.device}")
        
        # Load embedding model with GPU support - using lighter model for better performance
        try:
            self.embedding_model = SentenceTransformer(model_name, device=self.device)
            self.logger.info(f"Loaded embedding model: {model_name}")
        except Exception as e:
            self.logger.warning(f"Failed to load {model_name}, falling back to all-MiniLM-L6-v2: {e}")
            # Fallback to a lighter model
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2", device=self.device)
        
        # Load pre-computed embeddings
        self.load_embeddings()
    
    def _check_gpu_memory(self) -> bool:
        """Check if GPU has sufficient memory for embeddings"""
        try:
            import torch
            if torch.cuda.is_available():
                gpu_memory = torch.cuda.get_device_properties(0).total_memory
                # Require at least 2GB for embedding operations
                return gpu_memory > 2 * 1024**3
            return False
        except Exception:
            return False
    
    def load_embeddings(self):
        """Load FAISS index and metadata with GPU optimization"""
        try:
            # Load FAISS index
            possible_index_names = ["faiss_index.bin", "faiss_index.index"]
            index_path = None
            
            for index_name in possible_index_names:
                potential_path = os.path.join(self.embeddings_dir, index_name)
                if os.path.exists(potential_path):
                    index_path = potential_path
                    break
            
            if not index_path:
                raise FileNotFoundError(f"FAISS index not found in {self.embeddings_dir}")
            
            self.index = faiss.read_index(index_path)
            
            # Try to move index to GPU if available and beneficial
            if self.device == 'cuda' and self.index.ntotal > 1000:  # Only for larger indexes
                try:
                    import torch
                    if torch.cuda.is_available() and hasattr(faiss, 'StandardGpuResources'):
                        gpu_id = 0
                        res = faiss.StandardGpuResources()
                        self.index = faiss.index_cpu_to_gpu(res, gpu_id, self.index)
                        self.logger.info(f"Moved FAISS index to GPU for faster search")
                    else:
                        self.logger.info("FAISS-GPU not available, using CPU version")
                except Exception as e:
                    self.logger.warning(f"Failed to move index to GPU: {e}")
            
            self.logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            
            # Load metadata with better error handling
            # Prefer pickle file for faster loading of large datasets
            metadata_json_path = os.path.join(self.embeddings_dir, "metadata.json")
            metadata_pkl_path = os.path.join(self.embeddings_dir, "metadata.pkl")
            
            metadata_loaded = False
            
            # Try pickle first (faster for large files)
            if os.path.exists(metadata_pkl_path):
                try:
                    self.logger.info("Loading metadata from pickle file (faster for large datasets)...")
                    
                    # Custom unpickler to handle missing classes
                    class CustomUnpickler(pickle.Unpickler):
                        def find_class(self, module, name):
                            # Handle ChunkMetadata from different modules
                            if name == 'ChunkMetadata':
                                return ChunkMetadata
                            return super().find_class(module, name)
                    
                    with open(metadata_pkl_path, 'rb') as f:
                        unpickler = CustomUnpickler(f)
                        self.metadata = unpickler.load()
                    
                    metadata_loaded = True
                    self.logger.info(f"Loaded {len(self.metadata)} metadata entries from pickle file")
                except Exception as e:
                    self.logger.warning(f"Failed to load pickle metadata: {e}")
            
            # Try JSON as fallback (slower but more portable)
            if not metadata_loaded and os.path.exists(metadata_json_path):
                try:
                    self.logger.info("Loading metadata from JSON file...")
                    self.logger.warning("JSON file is large (4.6GB), this may take several minutes...")
                    
                    # For very large JSON files, we might need to process in chunks
                    file_size = os.path.getsize(metadata_json_path) / (1024 * 1024 * 1024)  # GB
                    if file_size > 3:  # If larger than 3GB
                        self.logger.warning(f"JSON file is {file_size:.1f}GB, this will take a while...")
                        self.logger.warning("Consider using the pickle file instead for faster loading")
                        # Set a timeout of 10 minutes for very large files
                        import signal
                        def timeout_handler(signum, frame):
                            raise TimeoutError("JSON loading timeout - file too large")
                        signal.signal(signal.SIGALRM, timeout_handler)
                        signal.alarm(600)  # 10 minutes timeout
                        
                        try:
                            with open(metadata_json_path, 'r', encoding='utf-8') as f:
                                self.metadata = json.load(f)
                        finally:
                            signal.alarm(0)  # Cancel timeout
                    else:
                        with open(metadata_json_path, 'r', encoding='utf-8') as f:
                            self.metadata = json.load(f)
                    
                    metadata_loaded = True
                    self.logger.info(f"Loaded {len(self.metadata)} metadata entries from JSON file")
                except (json.JSONDecodeError, UnicodeDecodeError, MemoryError, TimeoutError) as e:
                    self.logger.warning(f"Failed to load JSON metadata: {e}")
                    if isinstance(e, TimeoutError):
                        self.logger.warning("JSON file is too large. Consider using pickle format or regenerating embeddings.")
            
            if not metadata_loaded:
                raise FileNotFoundError("No valid metadata found")
            
            self.logger.info(f"Loaded metadata for {len(self.metadata)} chunks")
            
        except Exception as e:
            self.logger.error(f"Error loading embeddings: {e}")
            # Create dummy data to allow system to continue running
            self.index = None
            self.metadata = []
            raise
    
    def retrieve_chunks(self, query: str, top_k: int = 5) -> List[DatabaseChunk]:
        """Retrieve top-k most relevant chunks for the query"""
        try:
            # Embed the query
            query_embedding = self.embedding_model.encode([query]).astype('float32')
            
            # Search in FAISS index
            distances, indices = self.index.search(query_embedding, top_k)
            
            # Prepare results
            results = []
            for distance, idx in zip(distances[0], indices[0]):
                if idx < len(self.metadata):
                    chunk_data = self.metadata[idx]
                    
                    chunk = DatabaseChunk(
                        chunk_text=chunk_data.get('chunk_text', ''),
                        source=chunk_data.get('source', ''),
                        title=chunk_data.get('title', ''),
                        chunk_id=chunk_data.get('chunk_id', str(idx)),
                        source_domain=chunk_data.get('source_domain', ''),
                        similarity_score=float(1 / (1 + distance)),
                        metadata=chunk_data
                    )
                    results.append(chunk)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error retrieving chunks: {e}")
            return []


class WebSearcher:
    """Searches the web for relevant information with content extraction"""
    
    def __init__(self, max_results: int = 5):
        self.max_results = max_results
        self.logger = logging.getLogger(__name__)
        
        if not HAS_DDGS:
            raise ImportError("duckduckgo-search is required for web searching")
    
    def search(self, query: str, num_results: Optional[int] = None) -> List[SearchResult]:
        """Search the web for the given query with enhanced content extraction"""
        if num_results is None:
            num_results = self.max_results
        
        try:
            with DDGS() as ddgs:
                results = []
                
                # Perform search with agriculture focus
                search_query = f"{query} agriculture farming"
                search_results = ddgs.text(
                    search_query,
                    max_results=num_results,
                    safesearch='moderate'
                )
                
                for result in search_results:
                    # Extract more complete content
                    title = result.get('title', '')
                    url = result.get('href', '')
                    snippet = result.get('body', '')
                    
                    # Try to get more content if available
                    full_content = self._extract_extended_content(result, snippet)
                    
                    search_result = SearchResult(
                        title=title,
                        url=url,
                        snippet=snippet,
                        content=full_content
                    )
                    results.append(search_result)
                
                self.logger.info(f"Found {len(results)} web results for: {query}")
                return results
                
        except Exception as e:
            self.logger.error(f"Error searching web: {e}")
            return []
    
    def _extract_extended_content(self, result: Dict, fallback_snippet: str) -> str:
        """Extract extended content from search result with web scraping"""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # Try to fetch and extract content from the actual webpage
            url = result.get('href', '')
            if url:
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        
                        # Extract text from paragraphs and main content areas
                        content_parts = []
                        
                        # Look for main content areas
                        for tag in soup.find_all(['p', 'div', 'article', 'section']):
                            text = tag.get_text(strip=True)
                            if len(text) > 50 and 'agriculture' in text.lower() or 'farming' in text.lower():
                                content_parts.append(text)
                        
                        if content_parts:
                            full_content = ' '.join(content_parts[:5])  # Top 5 relevant paragraphs
                            # Truncate to reasonable length
                            return full_content[:2000] if len(full_content) > 2000 else full_content
                
                except Exception as e:
                    self.logger.debug(f"Web scraping failed for {url}: {e}")
            
            # Fallback to improving the snippet
            content_parts = []
            
            # Add main snippet
            if fallback_snippet:
                content_parts.append(fallback_snippet)
            
            # Look for additional content in result
            if 'content' in result and result['content']:
                content_parts.append(result['content'])
            
            # Look for description or summary
            if 'description' in result and result['description']:
                content_parts.append(result['description'])
            
            # Combine and clean content
            full_content = ' '.join(content_parts)
            
            # Remove duplicates and clean up
            sentences = full_content.split('.')
            unique_sentences = []
            seen = set()
            
            for sentence in sentences:
                cleaned = sentence.strip()
                if cleaned and cleaned not in seen and len(cleaned) > 20:
                    unique_sentences.append(cleaned)
                    seen.add(cleaned)
            
            return '. '.join(unique_sentences[:10])  # Limit to top 10 sentences
            
        except Exception as e:
            self.logger.warning(f"Content extraction failed: {e}")
            return fallback_snippet


class MarkdownGenerator:
    """Generates markdown reports from search results"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_markdown(self, sub_query_results: List[SubQueryResult], original_query: str) -> str:
        """Generate comprehensive markdown report with complete content"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        markdown = f"""# Agriculture Research Report

**Original Query:** {original_query}
**Generated:** {timestamp}
**Sub-queries Processed:** {len(sub_query_results)}

---

"""
        
        for i, result in enumerate(sub_query_results, 1):
            markdown += f"## Sub-query {i}: {result.original_query}\n\n"
            
            # Database results section with complete content
            if result.db_results:
                markdown += "### 📚 Database Results\n\n"
                for j, chunk in enumerate(result.db_results, 1):
                    markdown += f"**{j}. [{chunk.title or 'Database Entry'}]**\n"
                    markdown += f"- **Source:** {chunk.source}\n"
                    if chunk.source_domain:
                        markdown += f"- **Domain:** {chunk.source_domain}\n"
                    markdown += f"- **Similarity Score:** {chunk.similarity_score:.3f}\n"
                    markdown += f"- **Chunk ID:** {chunk.chunk_id}\n"
                    markdown += f"- **Full Content:**\n\n{chunk.chunk_text}\n\n"
                    markdown += f"- **Source Citation:** `[DB-{i}-{j}] {chunk.source}`\n\n"
                    markdown += "---\n\n"
            
            # Web results section with complete content
            if result.web_results:
                markdown += "### 🌐 Web Search Results\n\n"
                for j, web_result in enumerate(result.web_results, 1):
                    markdown += f"**{j}. [{web_result.title}]({web_result.url})**\n"
                    markdown += f"- **URL:** {web_result.url}\n"
                    markdown += f"- **Timestamp:** {datetime.fromtimestamp(web_result.timestamp).strftime('%Y-%m-%d %H:%M:%S')}\n"
                    if web_result.content:
                        markdown += f"- **Full Content:**\n\n{web_result.content}\n\n"
                    else:
                        markdown += f"- **Summary:**\n\n{web_result.snippet}\n\n"
                    markdown += f"- **Source Citation:** `[WEB-{i}-{j}] {web_result.title} - {web_result.url}`\n\n"
                    markdown += "---\n\n"
            
            markdown += "---\n\n"
        
        # Create citation index
        markdown += "## 📖 Citation Index\n\n"
        citation_count = 0
        for i, result in enumerate(sub_query_results, 1):
            for j, chunk in enumerate(result.db_results, 1):
                citation_count += 1
                markdown += f"{citation_count}. `[DB-{i}-{j}]` - {chunk.source} (Database)\n"
            for j, web_result in enumerate(result.web_results, 1):
                citation_count += 1
                markdown += f"{citation_count}. `[WEB-{i}-{j}]` - {web_result.title} ({web_result.url})\n"
        
        # Summary statistics
        total_db_results = sum(len(r.db_results) for r in sub_query_results)
        total_web_results = sum(len(r.web_results) for r in sub_query_results)
        
        markdown += f"""

## 📊 Summary Statistics

- **Total Database Chunks Retrieved:** {total_db_results}
- **Total Web Results Retrieved:** {total_web_results}
- **Sub-queries Generated:** {len(sub_query_results)}
- **Total Citations Available:** {citation_count}

---

*Report generated by Enhanced RAG System*
"""
        
        return markdown


class AnswerSynthesizer:
    """Synthesizes final answer using LLM"""
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
        self.logger = logging.getLogger(__name__)
    
    def get_available_models(self) -> List[str]:
        """Get list of available Ollama models using ollama list command"""
        try:
            # First try using ollama command line
            import subprocess
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                models = []
                for line in lines[1:]:  # Skip header line
                    if line.strip():
                        # Extract model name (first column)
                        model_name = line.split()[0]
                        if model_name and ':' in model_name:
                            models.append(model_name)
                self.logger.info(f"Found {len(models)} models via ollama list")
                return models
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
            self.logger.warning(f"ollama list command failed: {e}, trying API")
        
        # Fallback to API method
        try:
            response = requests.get(f'{self.ollama_host}/api/tags', timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                self.logger.info(f"Found {len(model_names)} models via API")
                return model_names
            return []
        except Exception as e:
            self.logger.error(f"Error getting available models: {e}")
            return ['llama3.2', 'llama3.1', 'qwen2.5']  # Default fallback models
    
    def synthesize_answer(self, original_query: str, markdown_content: str, model: str = "gemma3:27b") -> str:
        """Synthesize final answer from markdown content with inline citations"""
        
        prompt = f"""You are an expert agricultural consultant. Based on the comprehensive research report below, provide a detailed and accurate answer to the user's question.

CRITICAL INSTRUCTIONS FOR CITATIONS:
1. You MUST include inline citations for every factual claim
2. Use the exact citation format provided in the research report (e.g., [DB-1-2], [WEB-2-1])
3. When citing database sources, use [DB-X-Y] format
4. When citing web sources, use [WEB-X-Y] format
5. Multiple citations can be combined like [DB-1-1][WEB-2-3]
6. Every sentence with factual information should have at least one citation
7. Do not make claims without proper citations from the provided sources

Additional Guidelines:
- Provide a comprehensive yet focused answer
- Structure your answer clearly with appropriate sections
- If information is insufficient, acknowledge the limitations
- Only use information from the provided research report
- Include a "References" section at the end listing all citations used

Research Report:
{markdown_content}

User's Original Question: {original_query}

Comprehensive Answer with Inline Citations:"""

        try:
            response = requests.post(
                f'{self.ollama_host}/api/generate',
                json={
                    'model': model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.1,
                        'top_p': 0.9,
                        'num_ctx': 8192
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                answer = response.json()['response'].strip()
                self.logger.info(f"Synthesized answer with citations using {model}")
                return answer
            else:
                return f"Error generating answer: {response.status_code}"
                
        except Exception as e:
            self.logger.error(f"Error synthesizing answer: {e}")
            return f"Error generating answer: {str(e)}"


class MultiAgentRetriever:
    """Multi-agent system for enhanced retrieval using specialized agents"""
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
        self.logger = logging.getLogger(__name__)
        
        # Define specialized agents for different aspects
        self.agents = {
            'crop_specialist': {
                'focus': 'crops, varieties, cultivation, planting',
                'expertise': 'plant breeding, seed selection, crop rotation'
            },
            'soil_expert': {
                'focus': 'soil health, nutrients, fertilizers, amendments',
                'expertise': 'soil chemistry, pH, organic matter, erosion'
            },
            'pest_manager': {
                'focus': 'pests, diseases, IPM, biological control',
                'expertise': 'insect control, fungal diseases, resistance'
            },
            'sustainability_advisor': {
                'focus': 'sustainable practices, organic farming, environment',
                'expertise': 'conservation, renewable energy, water management'
            }
        }
    
    def retrieve_with_agents(self, query: str, sub_queries: List[str]) -> List[Dict[str, Any]]:
        """Use specialized agents to enhance retrieval"""
        try:
            enhanced_results = []
            
            for sub_query in sub_queries:
                # Determine best agent for this sub-query
                best_agent = self._select_best_agent(sub_query)
                
                # Generate agent-specific enhanced query
                enhanced_query = self._enhance_query_with_agent(sub_query, best_agent)
                
                # Store the enhanced query and agent info
                enhanced_results.append({
                    'original_query': sub_query,
                    'enhanced_query': enhanced_query,
                    'agent': best_agent,
                    'agent_focus': self.agents[best_agent]['focus'],
                    'agent_expertise': self.agents[best_agent]['expertise']
                })
            
            return enhanced_results
            
        except Exception as e:
            self.logger.error(f"Multi-agent retrieval failed: {e}")
            return []
    
    def _select_best_agent(self, query: str) -> str:
        """Select the best agent based on query content"""
        query_lower = query.lower()
        
        # Score each agent based on keyword matching
        scores = {}
        for agent_name, agent_info in self.agents.items():
            score = 0
            focus_keywords = agent_info['focus'].lower().split(', ')
            expertise_keywords = agent_info['expertise'].lower().split(', ')
            
            for keyword in focus_keywords:
                if keyword in query_lower:
                    score += 2
            
            for keyword in expertise_keywords:
                if keyword in query_lower:
                    score += 1
            
            scores[agent_name] = score
        
        # Return agent with highest score, default to crop_specialist
        best_agent = max(scores.items(), key=lambda x: x[1])[0]
        return best_agent if scores[best_agent] > 0 else 'crop_specialist'
    
    def _enhance_query_with_agent(self, query: str, agent: str) -> str:
        """Enhance query with agent-specific knowledge"""
        agent_info = self.agents[agent]
        
        # Add agent-specific context to the query
        enhanced_query = f"{query} {agent_info['focus']} {agent_info['expertise']}"
        
        return enhanced_query


class EnhancedRAGSystem:
    """Main enhanced RAG system combining database and web search"""
    
    def __init__(self, 
                 embeddings_dir: Optional[str] = None,
                 ollama_host: str = "http://localhost:11434",
                 temp_dir: Optional[str] = None):
        
        if embeddings_dir is None:
            # Default to relative path
            embeddings_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'agriculture_embeddings')
        
        self.embeddings_dir = embeddings_dir
        self.ollama_host = ollama_host
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.query_refiner = QueryRefiner(ollama_host)
        self.sub_query_generator = SubQueryGenerator(ollama_host)
        self.db_retriever = DatabaseRetriever(embeddings_dir)
        self.web_searcher = WebSearcher()
        self.markdown_generator = MarkdownGenerator()
        self.answer_synthesizer = AnswerSynthesizer(ollama_host)
        
        # Initialize multi-agent system
        try:
            self.multi_agent_retriever = MultiAgentRetriever(ollama_host)
            self.logger.info("Multi-agent retrieval system initialized")
        except Exception as e:
            self.logger.warning(f"Multi-agent system not available: {e}")
            self.multi_agent_retriever = None
    
    def process_query(self, 
                     user_query: str,
                     num_sub_queries: int = 3,
                     db_chunks_per_query: int = 3,
                     web_results_per_query: int = 3,
                     synthesis_model: str = "gemma3:27b",
                     enable_database_search: bool = True,
                     enable_web_search: bool = True) -> Dict[str, Any]:
        """Process user query through the complete RAG pipeline with toggles"""
        
        start_time = datetime.now()
        self.logger.info(f"Processing query: {user_query}")
        self.logger.info(f"Database search: {'enabled' if enable_database_search else 'disabled'}")
        self.logger.info(f"Web search: {'enabled' if enable_web_search else 'disabled'}")
        
        # Validate that at least one search method is enabled
        if not enable_database_search and not enable_web_search:
            return {
                'error': 'At least one search method (database or web) must be enabled',
                'original_query': user_query,
                'processing_time': 0
            }
        
        # Step 1: Refine the query
        refined_query = self.query_refiner.refine_query(user_query)
        
        # Step 2: Generate sub-queries
        sub_queries = self.sub_query_generator.generate_sub_queries(refined_query, num_sub_queries)
        
        # Step 3: Process each sub-query
        sub_query_results = []
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all sub-query processing tasks
            future_to_query = {}
            
            for sub_query in sub_queries:
                future = executor.submit(
                    self._process_sub_query, 
                    sub_query, 
                    db_chunks_per_query if enable_database_search else 0, 
                    web_results_per_query if enable_web_search else 0,
                    enable_database_search,
                    enable_web_search
                )
                future_to_query[future] = sub_query
            
            # Collect results
            for future in as_completed(future_to_query):
                sub_query = future_to_query[future]
                try:
                    result = future.result()
                    sub_query_results.append(result)
                except Exception as e:
                    self.logger.error(f"Error processing sub-query '{sub_query}': {e}")
                    # Add empty result
                    sub_query_results.append(SubQueryResult(sub_query, [sub_query]))
        
        # Step 4: Generate markdown report
        markdown_content = self.markdown_generator.generate_markdown(sub_query_results, user_query)
        
        # Step 5: Save markdown to temp file
        temp_file_path = os.path.join(self.temp_dir, f"rag_report_{int(datetime.now().timestamp())}.md")
        with open(temp_file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # Step 6: Synthesize final answer
        final_answer = self.answer_synthesizer.synthesize_answer(user_query, markdown_content, synthesis_model)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'original_query': user_query,
            'refined_query': refined_query,
            'sub_queries': sub_queries,
            'sub_query_results': sub_query_results,
            'markdown_content': markdown_content,
            'markdown_file_path': temp_file_path,
            'final_answer': final_answer,
            'synthesis_model': synthesis_model,
            'processing_time': processing_time,
            'search_settings': {
                'database_search_enabled': enable_database_search,
                'web_search_enabled': enable_web_search,
                'db_chunks_per_query': db_chunks_per_query if enable_database_search else 0,
                'web_results_per_query': web_results_per_query if enable_web_search else 0
            },
            'stats': {
                'total_db_chunks': sum(len(r.db_results) for r in sub_query_results),
                'total_web_results': sum(len(r.web_results) for r in sub_query_results),
                'num_sub_queries': len(sub_queries)
            }
        }
    
    def _process_sub_query(self, sub_query: str, db_chunks: int, web_results: int, 
                          enable_db: bool = True, enable_web: bool = True) -> SubQueryResult:
        """Process a single sub-query to get database and web results with multi-agent enhancement"""
        
        # Use multi-agent enhancement if available
        enhanced_query = sub_query
        agent_info = {}
        
        if self.multi_agent_retriever:
            try:
                agent_enhancements = self.multi_agent_retriever.retrieve_with_agents(sub_query, [sub_query])
                if agent_enhancements:
                    enhancement = agent_enhancements[0]
                    enhanced_query = enhancement['enhanced_query']
                    agent_info = {
                        'agent': enhancement['agent'],
                        'agent_focus': enhancement['agent_focus'],
                        'agent_expertise': enhancement['agent_expertise']
                    }
                    self.logger.info(f"Enhanced query using {enhancement['agent']}: {enhanced_query}")
            except Exception as e:
                self.logger.warning(f"Multi-agent enhancement failed: {e}")
        
        db_results = []
        web_results_list = []
        
        # Get database results if enabled (use enhanced query)
        if enable_db and db_chunks > 0:
            try:
                db_results = self.db_retriever.retrieve_chunks(enhanced_query, db_chunks)
                self.logger.info(f"Retrieved {len(db_results)} database chunks for: {enhanced_query}")
            except Exception as e:
                self.logger.error(f"Database retrieval failed for '{enhanced_query}': {e}")
        
        # Get web results if enabled (use enhanced query)
        if enable_web and web_results > 0:
            try:
                web_results_list = self.web_searcher.search(enhanced_query, web_results)
                self.logger.info(f"Retrieved {len(web_results_list)} web results for: {enhanced_query}")
            except Exception as e:
                self.logger.error(f"Web search failed for '{enhanced_query}': {e}")
        
        result = SubQueryResult(
            original_query=sub_query,
            sub_queries=[sub_query],
            web_results=web_results_list,
            db_results=db_results
        )
        
        # Add agent information if available
        if agent_info:
            result.agent_info = agent_info
        
        return result
    
    def get_available_synthesis_models(self) -> List[str]:
        """Get available models for synthesis"""
        return self.answer_synthesizer.get_available_models()


def setup_logging(level=logging.INFO):
    """Setup logging configuration"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


# Test function
if __name__ == "__main__":
    # Setup logging
    setup_logging()
    
    # Initialize the system
    embeddings_dir = "/store/Answering_Agriculture/agriculture_embeddings"
    
    try:
        rag_system = EnhancedRAGSystem(embeddings_dir)
        
        # Test query
        result = rag_system.process_query(
            "What are the best practices for wheat cultivation?",
            num_sub_queries=2,
            db_chunks_per_query=3,
            web_results_per_query=2
        )
        
        print("=== ENHANCED RAG RESULT ===")
        print(f"Original Query: {result['original_query']}")
        print(f"Refined Query: {result['refined_query']}")
        print(f"Sub-queries: {result['sub_queries']}")
        print(f"Processing Time: {result['processing_time']:.2f}s")
        print(f"Final Answer: {result['final_answer'][:500]}...")
        print(f"Markdown saved to: {result['markdown_file_path']}")
        
    except Exception as e:
        print(f"Error: {e}")
