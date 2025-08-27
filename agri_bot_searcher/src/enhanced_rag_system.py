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

# Import torch
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

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
        
        prompt = f"""You are an agricultural AI assistant. Transform the user's query into a more specific and searchable agricultural query while preserving their intent.

Rules:
1. Understand the context and agricultural issue being described
2. Make reasonable assumptions about common agricultural scenarios
3. Transform it into a clear, searchable query
4. Keep the original intent and urgency
5. Add relevant agricultural keywords
6. Return ONLY the refined query, no explanations

Examples:
- "My crops are dying" → "crop disease symptoms identification and treatment for dying plants"
- "Rain damaged my field" → "monsoon crop damage assessment and government compensation schemes in India"
- "Need money for farming" → "agricultural loans subsidies and financial assistance programs for farmers"

User query: {query}

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
        
        prompt = f"""Break down this agricultural query into {num_queries} specific search queries.

Create focused, natural language search queries (NOT SQL) that cover different aspects:
1. Direct problem/solution search
2. Government policies/schemes related to the issue  
3. Technical/scientific information about the agricultural issue

Main query: {query}

Generate {num_queries} concise search queries (one per line):"""

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
                        # Remove quotes and extra formatting
                        clean_query = clean_query.strip('"').strip("'").strip('*').strip()
                        if clean_query and len(clean_query) > 10 and not clean_query.lower().startswith(('here are', 'okay', 'the following')):
                            sub_queries.append(clean_query)
                
                if not sub_queries:
                    # Fallback: split by lines and take meaningful ones
                    for line in lines:
                        line = line.strip()
                        if line and len(line) > 15 and not line.lower().startswith(('here are', 'okay', 'the following')):
                            # Clean up any remaining formatting
                            clean_line = line.strip('"').strip("'").strip('*').strip()
                            sub_queries.append(clean_line)
                
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
    
    def __init__(self, embeddings_dir: str, model_name: str = "Qwen/Qwen3-Embedding-8B"):
        self.embeddings_dir = embeddings_dir
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)
        
        if not HAS_SENTENCE_TRANSFORMERS:
            raise ImportError("sentence-transformers is required for database retrieval")
        
        # Determine device (GPU if available) with memory check
        self.device = 'cuda' if HAS_TORCH and torch.cuda.is_available() and self._check_gpu_memory() else 'cpu'
        self.logger.info(f"Using device: {self.device}")
        
        # Load embedding model with GPU support
        self.embedding_model = SentenceTransformer(model_name, device=self.device)
        
        # Load pre-computed embeddings
        self.load_embeddings()
    
    def _check_gpu_memory(self) -> bool:
        """Check if GPU has sufficient memory for embeddings"""
        try:
            if HAS_TORCH and torch.cuda.is_available():
                gpu_memory = torch.cuda.get_device_properties(0).total_memory
                # Require at least 2GB for embedding operations
                return gpu_memory > 2 * 1024**3
            return False
        except Exception:
            return False
    
    def load_embeddings(self):
        """Load FAISS index and metadata with improved error handling and optimization"""
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
            
            self.logger.info(f"Loading FAISS index from {index_path}")
            self.index = faiss.read_index(index_path)
            
            # Try to move index to GPU if available and beneficial
            if self.device == 'cuda' and self.index.ntotal > 1000:  # Only for larger indexes
                try:
                    import torch
                    if HAS_TORCH and torch.cuda.is_available() and hasattr(faiss, 'StandardGpuResources'):
                        gpu_id = 0
                        res = faiss.StandardGpuResources()
                        self.index = faiss.index_cpu_to_gpu(res, gpu_id, self.index)
                        self.logger.info(f"Moved FAISS index to GPU for faster search")
                    else:
                        self.logger.info("FAISS-GPU not available, using CPU version")
                except Exception as e:
                    self.logger.warning(f"Failed to move index to GPU: {e}")
            
            self.logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            
            # Load metadata with improved handling for large files
            metadata_pkl_path = os.path.join(self.embeddings_dir, "metadata.pkl")
            metadata_json_path = os.path.join(self.embeddings_dir, "metadata.json")
            
            # Try pickle first (much faster)
            if os.path.exists(metadata_pkl_path):
                try:
                    self.logger.info("Loading metadata from pickle file...")
                    with open(metadata_pkl_path, 'rb') as f:
                        self.metadata = pickle.load(f)
                    self.logger.info(f"Successfully loaded metadata for {len(self.metadata)} chunks from pickle")
                except Exception as pickle_error:
                    self.logger.warning(f"Failed to load pickle metadata: {pickle_error}")
                    self.metadata = None
            
            # Fallback to JSON if pickle failed or doesn't exist
            if self.metadata is None and os.path.exists(metadata_json_path):
                try:
                    # Check file size first
                    file_size = os.path.getsize(metadata_json_path)
                    file_size_gb = file_size / (1024**3)
                    
                    if file_size_gb > 1.0:
                        self.logger.warning(f"JSON file is large ({file_size_gb:.1f}GB), this may take several minutes...")
                        self.logger.warning(f"JSON file is {file_size_gb:.1f}GB, this will take a while...")
                        self.logger.warning("Consider using the pickle file instead for faster loading")
                    
                    self.logger.info("Loading metadata from JSON file...")
                    with open(metadata_json_path, 'r', encoding='utf-8') as f:
                        self.metadata = json.load(f)
                    self.logger.info(f"Successfully loaded metadata for {len(self.metadata)} chunks from JSON")
                    
                    # Create pickle file for faster future loading
                    self.logger.info("Creating pickle file for faster future loading...")
                    try:
                        with open(metadata_pkl_path, 'wb') as f:
                            pickle.dump(self.metadata, f)
                        self.logger.info("Created pickle file for faster loading next time")
                    except Exception as pickle_save_error:
                        self.logger.warning(f"Failed to save pickle file: {pickle_save_error}")
                        
                except Exception as json_error:
                    self.logger.error(f"Failed to load JSON metadata: {json_error}")
                    raise FileNotFoundError("Could not load metadata from either pickle or JSON files")
            
            if self.metadata is None:
                raise FileNotFoundError("No valid metadata file found")
            
            # Validate metadata compatibility with FAISS index
            if len(self.metadata) != self.index.ntotal:
                self.logger.warning(f"Metadata count ({len(self.metadata)}) doesn't match FAISS index count ({self.index.ntotal})")
                self.logger.info(f"Using the smaller count for safety: min({len(self.metadata)}, {self.index.ntotal}) = {min(len(self.metadata), self.index.ntotal)}")
                # Adjust search parameters to work with available data
                self.max_safe_index = min(len(self.metadata), self.index.ntotal) - 1
            
            self.logger.info(f"Successfully loaded embeddings system with {self.index.ntotal} vectors and {len(self.metadata)} metadata entries")
            
            # Set max_safe_index if not already set
            if not hasattr(self, 'max_safe_index'):
                self.max_safe_index = min(len(self.metadata), self.index.ntotal) - 1
            
        except Exception as e:
            self.logger.error(f"Error loading embeddings: {e}")
            raise
    
    def retrieve_chunks(self, query: str, top_k: int = 5) -> List[DatabaseChunk]:
        """Retrieve top-k most relevant chunks for the query with improved error handling"""
        try:
            if not hasattr(self, 'index') or self.index is None:
                self.logger.error("FAISS index not loaded")
                return []
            
            if not hasattr(self, 'metadata') or self.metadata is None:
                self.logger.error("Metadata not loaded")
                return []
            
            # Embed the query
            query_embedding = self.embedding_model.encode([query]).astype('float32')
            
            # Normalize for cosine similarity if the index expects it
            import faiss
            faiss.normalize_L2(query_embedding)
            
            # Search in FAISS index
            try:
                # Adjust top_k to not exceed available data
                safe_top_k = min(top_k, self.index.ntotal)
                if hasattr(self, 'max_safe_index'):
                    safe_top_k = min(safe_top_k, self.max_safe_index + 1)
                
                distances, indices = self.index.search(query_embedding, safe_top_k)
            except Exception as search_error:
                self.logger.error(f"Error searching FAISS index: {search_error}")
                return []
            
            # Prepare results
            results = []
            for distance, idx in zip(distances[0], indices[0]):
                try:
                    # Enhanced bounds checking
                    if idx < 0:
                        self.logger.warning(f"Negative index {idx}, skipping")
                        continue
                    
                    if idx >= len(self.metadata):
                        self.logger.warning(f"Index {idx} exceeds metadata bounds ({len(self.metadata)}), skipping")
                        continue
                    
                    # Additional safety check for max_safe_index
                    if hasattr(self, 'max_safe_index') and idx > self.max_safe_index:
                        self.logger.warning(f"Index {idx} exceeds safe bounds ({self.max_safe_index}), skipping")
                        continue
                        
                    chunk_data = self.metadata[idx]
                    
                    # Handle both dict and object metadata formats
                    if isinstance(chunk_data, dict):
                        chunk_text = chunk_data.get('chunk_text', '')
                        source = chunk_data.get('link', chunk_data.get('source', ''))
                        title = chunk_data.get('title', '')
                        chunk_id = chunk_data.get('chunk_id', str(idx))
                        source_domain = chunk_data.get('source_domain', '')
                    else:
                        # Handle object format (from pickle)
                        chunk_text = getattr(chunk_data, 'chunk_text', '')
                        source = getattr(chunk_data, 'link', getattr(chunk_data, 'source', ''))
                        title = getattr(chunk_data, 'title', '')
                        chunk_id = getattr(chunk_data, 'chunk_id', str(idx))
                        source_domain = getattr(chunk_data, 'source_domain', '')
                    
                    if not chunk_text:
                        self.logger.warning(f"Empty chunk text for index {idx}, skipping")
                        continue
                    
                    chunk = DatabaseChunk(
                        chunk_text=chunk_text,
                        source=source,
                        title=title,
                        chunk_id=str(chunk_id),
                        source_domain=source_domain,
                        similarity_score=float(1 / (1 + distance)) if distance >= 0 else 0.0,
                        metadata=chunk_data if isinstance(chunk_data, dict) else {}
                    )
                    results.append(chunk)
                    
                except Exception as chunk_error:
                    self.logger.warning(f"Error processing chunk {idx}: {chunk_error}")
                    continue
            
            self.logger.info(f"Retrieved {len(results)} chunks for query: {query[:50]}...")
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
    
    def generate_comprehensive_markdown(self, original_query: str, refined_query: str, 
                                       sub_queries: List[str], sub_query_results: List[SubQueryResult]) -> str:
        """Generate comprehensive markdown report with all pipeline information"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        markdown = f"""# Enhanced RAG Agriculture Research Report

**Original Query:** {original_query}
**Refined Query:** {refined_query}
**Generated:** {timestamp}
**Pipeline Steps:** Query Refinement → Sub-query Generation → Multi-source Retrieval → Content Synthesis

---

## 🔍 Query Processing Pipeline

### 1. Original User Query
```
{original_query}
```

### 2. Refined Query
```
{refined_query}
```

### 3. Generated Sub-queries ({len(sub_queries)})
"""
        for i, sub_query in enumerate(sub_queries, 1):
            markdown += f"{i}. {sub_query}\n"
        
        markdown += "\n---\n\n"
        
        # Process each sub-query result
        for i, result in enumerate(sub_query_results, 1):
            markdown += f"## Sub-query {i}: {result.original_query}\n\n"
            
            # Add agent info if available
            if result.agent_info:
                markdown += f"**Agent Enhancement:** {result.agent_info}\n\n"
            
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

- **Original Query:** {original_query}
- **Refined Query:** {refined_query}
- **Total Sub-queries Generated:** {len(sub_queries)}
- **Total Database Chunks Retrieved:** {total_db_results}
- **Total Web Results Retrieved:** {total_web_results}
- **Total Citations Available:** {citation_count}

---

*Comprehensive report generated by Enhanced RAG System*
"""
        
        return markdown


class AnswerSynthesizer:
    """Synthesizes final answer using LLM"""
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
        self.logger = logging.getLogger(__name__)
    
    def get_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            response = requests.get(f'{self.ollama_host}/api/tags', timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
            return []
        except Exception as e:
            self.logger.error(f"Error getting available models: {e}")
            return []
    
    def synthesize_answer(self, original_query: str, markdown_content: str, model: str = "gemma3:27b") -> str:
        """Synthesize final answer from markdown content with inline citations"""
        
        # Optimize context size for large models to prevent timeouts
        optimized_content = markdown_content
        if '27b' in model.lower() or '70b' in model.lower():
            # For very large models, truncate content if it's extremely long to prevent timeouts
            if len(markdown_content) > 30000:  # ~30KB limit for large models
                self.logger.warning(f"Truncating markdown content from {len(markdown_content)} to 30000 chars for large model {model}")
                optimized_content = markdown_content[:30000] + "\n\n[Content truncated for processing efficiency - full content available in markdown tab]"
        
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
{optimized_content}

User's Original Question: {original_query}

Comprehensive Answer with Inline Citations:"""

        try:
            # Enhanced timeout calculation for larger models
            if '70b' in model.lower() or '72b' in model.lower():
                timeout_seconds = 900  # 15 minutes for 70B+ models
            elif '27b' in model.lower() or '30b' in model.lower():
                timeout_seconds = 720  # 12 minutes for 27B-30B models (was 8 min)
            elif '13b' in model.lower() or '14b' in model.lower():
                timeout_seconds = 480  # 8 minutes for 13B-14B models (was 5 min)
            elif '7b' in model.lower() or '8b' in model.lower():
                timeout_seconds = 300  # 5 minutes for 7B-8B models (was 3 min)
            else:
                timeout_seconds = 180  # 3 minutes for smaller models (was 2 min)
            
            self.logger.info(f"Using {timeout_seconds}s timeout for model {model}")
            
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
                timeout=timeout_seconds
            )
            
            if response.status_code == 200:
                answer = response.json()['response'].strip()
                self.logger.info(f"Synthesized answer with citations using {model}")
                return answer
            else:
                return f"Error generating answer: {response.status_code}"
                
        except Exception as e:
            self.logger.error(f"Error synthesizing answer: {e}")
            # Enhanced fallback handling with timeout-specific messaging
            if "Read timed out" in str(e) or "timeout" in str(e).lower():
                return f"""**⏱️ Processing Timeout Notice**

The AI synthesis step timed out after {timeout_seconds} seconds due to the computational requirements of the large model `{model}`. However, comprehensive research has been completed.

**📊 Research Summary:**
- Database chunks retrieved and analyzed
- Web search results gathered and processed  
- Information synthesized into structured report

**🔍 Complete Research Report:**

{markdown_content[:3000]}...

*[Report continues in the Pipeline Info and Full Markdown tabs]*

**💡 Recommendations:**
- Switch to a smaller model (e.g., llama3.2:3b, gemma2:9b) for faster responses
- Review the complete research in the "Full Markdown" tab
- The retrieved information is comprehensive and ready for analysis

**📚 Note**: All retrieved information, citations, and detailed pipeline information are available in the respective tabs above."""
            else:
                return f"""**❌ Processing Error**

An error occurred during AI synthesis: {str(e)}

**📋 Fallback Information Available:**
Please check the following tabs for complete research data:
- **Pipeline Info**: Detailed processing steps and debug information
- **Full Markdown**: Complete structured research report  
- **Citations**: Source references and links

**🔧 Troubleshooting:**
- Verify that Ollama is running: `ollama serve`
- Check if the model is available: `ollama list`
- Try a different model if the current one is unavailable

The research and retrieval phases completed successfully - only the final synthesis step encountered issues."""


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
        
        # Initialize components with error handling
        self.query_refiner = QueryRefiner(ollama_host)
        self.sub_query_generator = SubQueryGenerator(ollama_host)
        
        # Try to initialize database retriever
        self.db_retriever = None
        self.db_available = False
        try:
            if os.path.exists(embeddings_dir):
                self.db_retriever = DatabaseRetriever(embeddings_dir)
                self.db_available = True
                self.logger.info("Database retriever initialized successfully")
            else:
                self.logger.warning(f"Embeddings directory not found: {embeddings_dir}")
        except Exception as e:
            self.logger.error(f"Failed to initialize database retriever: {e}")
            self.logger.info("RAG system will continue with web search only")
        
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
        print(f"\n🔍 Starting Enhanced RAG Pipeline")
        print(f"📝 Original Query: {user_query}")
        print(f"⚙️ Parameters:")
        print(f"   - Sub-queries: {num_sub_queries}")
        print(f"   - DB chunks per query: {db_chunks_per_query}")
        print(f"   - Web results per query: {web_results_per_query}")
        print(f"   - Synthesis model: {synthesis_model}")
        print(f"   - Database search: {'✅ enabled' if enable_database_search else '❌ disabled'}")
        print(f"   - Web search: {'✅ enabled' if enable_web_search else '❌ disabled'}")
        
        self.logger.info(f"Processing query: {user_query}")
        self.logger.info(f"Database search: {'enabled' if enable_database_search else 'disabled'}")
        self.logger.info(f"Web search: {'enabled' if enable_web_search else 'disabled'}")
        
        # Validate that at least one search method is enabled and available
        if not enable_database_search and not enable_web_search:
            error_msg = 'At least one search method (database or web) must be enabled'
            print(f"❌ Error: {error_msg}")
            return {
                'error': error_msg,
                'original_query': user_query,
                'processing_time': 0
            }
        
        # Check if database search is requested but not available
        if enable_database_search and not self.db_available:
            print("⚠️ Warning: Database search requested but database not available, using web search only")
            self.logger.warning("Database search requested but database not available, using web search only")
            enable_database_search = False
            
        # Ensure at least web search is available if database is not
        if not enable_database_search and not enable_web_search:
            error_msg = 'No search methods available (database failed to load and web search disabled)'
            print(f"❌ Error: {error_msg}")
            return {
                'error': error_msg,
                'original_query': user_query,
                'processing_time': 0
            }
        
        # Step 1: Refine the query
        print(f"\n🔧 Step 1: Refining query...")
        refined_query = self.query_refiner.refine_query(user_query)
        print(f"✨ Refined Query: {refined_query}")
        
        # Step 2: Generate sub-queries
        print(f"\n🔗 Step 2: Generating {num_sub_queries} sub-queries...")
        sub_queries = self.sub_query_generator.generate_sub_queries(refined_query, num_sub_queries)
        print(f"📋 Generated Sub-queries:")
        for i, sq in enumerate(sub_queries, 1):
            print(f"   {i}. {sq}")
        
        # Step 3: Process each sub-query
        print(f"\n🔍 Step 3: Processing sub-queries...")
        sub_query_results = []
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all sub-query processing tasks
            future_to_query = {}
            
            for i, sub_query in enumerate(sub_queries, 1):
                print(f"⚡ Submitting sub-query {i} for processing...")
                future = executor.submit(
                    self._process_sub_query, 
                    sub_query, 
                    db_chunks_per_query if enable_database_search else 0, 
                    web_results_per_query if enable_web_search else 0,
                    enable_database_search,
                    enable_web_search
                )
                future_to_query[future] = (i, sub_query)
            
            # Collect results
            for future in as_completed(future_to_query):
                query_num, sub_query = future_to_query[future]
                try:
                    print(f"📥 Collecting results for sub-query {query_num}...")
                    result = future.result()
                    sub_query_results.append(result)
                    
                    # Log results for this sub-query
                    db_count = len(result.db_results) if hasattr(result, 'db_results') else 0
                    web_count = len(result.web_results) if hasattr(result, 'web_results') else 0
                    print(f"   Sub-query {query_num}: {db_count} DB chunks, {web_count} web results")
                    
                except Exception as e:
                    print(f"❌ Error processing sub-query {query_num}: {e}")
                    self.logger.error(f"Error processing sub-query '{sub_query}': {e}")
        
        # Step 4: Generate comprehensive markdown report
        print(f"\n📄 Step 4: Generating comprehensive markdown report...")
        markdown_content = self.markdown_generator.generate_comprehensive_markdown(
            original_query=user_query,
            refined_query=refined_query,
            sub_queries=sub_queries,
            sub_query_results=sub_query_results
        )
        
        # Save markdown to temporary file
        temp_file_path = None
        try:
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md', encoding='utf-8')
            temp_file.write(markdown_content)
            temp_file.close()
            temp_file_path = temp_file.name
            print(f"💾 Markdown report saved to: {temp_file_path}")
        except Exception as e:
            print(f"⚠️ Warning: Could not save markdown file: {e}")
            self.logger.warning(f"Could not save markdown file: {e}")
        
        # Step 5: Synthesize final answer
        print(f"\n🤖 Step 5: Synthesizing final answer using {synthesis_model}...")
        final_answer = self.answer_synthesizer.synthesize_answer(
            original_query=user_query,
            markdown_content=markdown_content,
            model=synthesis_model
        )
        
        # Calculate processing time and statistics
        processing_time = (datetime.now() - start_time).total_seconds()
        total_db_chunks = sum(len(r.db_results) for r in sub_query_results)
        total_web_results = sum(len(r.web_results) for r in sub_query_results)
        
        print(f"\n✅ Pipeline completed successfully!")
        print(f"⏱️ Total processing time: {processing_time:.2f} seconds")
        print(f"📊 Final Statistics:")
        print(f"   - Total database chunks retrieved: {total_db_chunks}")
        print(f"   - Total web results retrieved: {total_web_results}")
        print(f"   - Sub-queries processed: {len(sub_queries)}")
        print(f"   - Final answer length: {len(final_answer)} characters")
        print(f"   - Markdown report length: {len(markdown_content)} characters")
        
        # Create comprehensive result structure
        result = {
            'success': True,
            'answer': final_answer,
            'original_query': user_query,
            'pipeline_info': {
                'refined_query': refined_query,
                'sub_queries': sub_queries,
                'sub_query_results': [
                    {
                        'query': r.original_query,
                        'db_chunks': len(r.db_results),
                        'web_results': len(r.web_results),
                        'agent_info': r.agent_info
                    } for r in sub_query_results
                ],
                'total_db_chunks': total_db_chunks,
                'total_web_results': total_web_results,
                'synthesis_model': synthesis_model,
                'search_settings': {
                    'database_search_enabled': enable_database_search,
                    'web_search_enabled': enable_web_search,
                    'db_chunks_per_query': db_chunks_per_query if enable_database_search else 0,
                    'web_results_per_query': web_results_per_query if enable_web_search else 0
                }
            },
            'markdown_content': markdown_content,
            'markdown_file_path': temp_file_path,
            'citations': self._extract_citations(sub_query_results),
            'processing_time': processing_time
        }
        
        return result
    
    def _extract_citations(self, sub_query_results: List[SubQueryResult]) -> List[Dict[str, Any]]:
        """Extract citations from sub-query results"""
        citations = []
        
        for i, result in enumerate(sub_query_results):
            # Database citations
            for j, db_result in enumerate(result.db_results):
                citations.append({
                    'type': 'database',
                    'id': f'DB-{i+1}-{j+1}',
                    'title': db_result.title or db_result.source,
                    'source': db_result.source,
                    'content_preview': db_result.chunk_text[:200] + "..." if len(db_result.chunk_text) > 200 else db_result.chunk_text,
                    'similarity_score': db_result.similarity_score
                })
            
            # Web citations
            for j, web_result in enumerate(result.web_results):
                citations.append({
                    'type': 'web',
                    'id': f'WEB-{i+1}-{j+1}',
                    'title': web_result.title,
                    'url': web_result.url,
                    'content_preview': web_result.snippet[:200] + "..." if len(web_result.snippet) > 200 else web_result.snippet,
                    'relevance_score': web_result.relevance_score
                })
        
        return citations
    
    def _process_sub_query(self, sub_query: str, db_chunks: int, web_results: int, 
                          enable_db: bool = True, enable_web: bool = True) -> SubQueryResult:
        """Process a single sub-query to get database and web results with multi-agent enhancement"""
        
        print(f"  🔍 Processing sub-query: {sub_query}")
        
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
                    print(f"    🤖 Enhanced by {enhancement['agent']}: {enhanced_query}")
                    self.logger.info(f"Enhanced query using {enhancement['agent']}: {enhanced_query}")
            except Exception as e:
                print(f"    ⚠️ Multi-agent enhancement failed: {e}")
                self.logger.warning(f"Multi-agent enhancement failed: {e}")
        
        db_results = []
        web_results_list = []
        
        # Get database results if enabled (use enhanced query)
        if enable_db and db_chunks > 0:
            try:
                print(f"    📚 Searching database for {db_chunks} chunks...")
                db_results = self.db_retriever.retrieve_chunks(enhanced_query, db_chunks)
                print(f"    ✅ Retrieved {len(db_results)} database chunks")
                self.logger.info(f"Retrieved {len(db_results)} database chunks for: {enhanced_query}")
            except Exception as e:
                print(f"    ❌ Database retrieval failed: {e}")
                self.logger.error(f"Database retrieval failed for '{enhanced_query}': {e}")
        
        # Get web results if enabled (use enhanced query)
        if enable_web and web_results > 0:
            try:
                print(f"    🌐 Searching web for {web_results} results...")
                web_results_list = self.web_searcher.search(enhanced_query, web_results)
                print(f"    ✅ Retrieved {len(web_results_list)} web results")
                self.logger.info(f"Retrieved {len(web_results_list)} web results for: {enhanced_query}")
            except Exception as e:
                print(f"    ❌ Web search failed: {e}")
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
    embeddings_dir = "/store/testing/Answering_Agriculture/agriculture_embeddings"
    
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
        print(f"Refined Query: {result.get('refined_query', 'N/A')}")
        print(f"Sub-queries: {result.get('sub_queries', [])}")
        print(f"Processing Time: {result.get('processing_time', 0):.2f}s")
        print(f"Final Answer: {result.get('answer', 'No answer')[:500]}...")
        print(f"Markdown saved to: {result.get('markdown_file_path', 'N/A')}")
        
    except Exception as e:
        print(f"Error: {e}")
