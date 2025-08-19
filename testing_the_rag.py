#!/usr/bin/env python3
"""
RAG (Retrieval-Augmented Generation) system using existing embeddings
and Ollama's Gemma3:27b model for answer generation
"""

import os
import json
import numpy as np
import faiss
import pickle
import requests
from typing import List, Dict, Any, Tuple
import argparse
from sentence_transformers import SentenceTransformer
import logging

class RAGSystem:
    def __init__(self, embeddings_dir: str, model_name: str = "Qwen/Qwen3-Embedding-8B", 
                 ollama_model: str = "gemma3:27b"):
        """
        Initialize RAG system with pre-computed embeddings
        
        Args:
            embeddings_dir: Directory containing the saved embeddings
            model_name: Name of the embedding model (should match the one used for creating embeddings)
            ollama_model: Ollama model name for generation
        """
        self.embeddings_dir = embeddings_dir
        self.ollama_model = ollama_model
        self.logger = logging.getLogger(__name__)
        
        # Load the embedding model (same as used for creating embeddings)
        self.logger.info(f"Loading embedding model: {model_name}")
        self.embedding_model = SentenceTransformer(model_name)
        
        # Load pre-computed embeddings and metadata
        self.load_embeddings()
        
    def load_embeddings(self):
        """Load FAISS index and metadata"""
        try:
            # Try different possible FAISS index filenames
            possible_index_names = ["faiss_index.bin", "faiss_index.index"]
            index_path = None
            
            for index_name in possible_index_names:
                potential_path = os.path.join(self.embeddings_dir, index_name)
                if os.path.exists(potential_path):
                    index_path = potential_path
                    break
            
            if not index_path:
                raise FileNotFoundError(f"FAISS index not found. Tried: {possible_index_names}")
            
            self.index = faiss.read_index(index_path)
            self.logger.info(f"Loaded FAISS index from {os.path.basename(index_path)} with {self.index.ntotal} vectors")
            
            # Load metadata - try both JSON and pickle formats
            metadata_json_path = os.path.join(self.embeddings_dir, "metadata.json")
            metadata_pkl_path = os.path.join(self.embeddings_dir, "metadata.pkl")
            
            if os.path.exists(metadata_json_path):
                with open(metadata_json_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                self.logger.info(f"Loaded metadata from JSON for {len(self.metadata)} chunks")
            elif os.path.exists(metadata_pkl_path):
                with open(metadata_pkl_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                self.logger.info(f"Loaded metadata from pickle for {len(self.metadata)} chunks")
            else:
                raise FileNotFoundError("Metadata not found. Expected metadata.json or metadata.pkl")
            
            # Load config if available
            config_path = os.path.join(self.embeddings_dir, "config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
                self.logger.info("Loaded configuration")
            else:
                self.config = None
            
            # Load summary stats if available
            stats_path = os.path.join(self.embeddings_dir, "summary_stats.json")
            if os.path.exists(stats_path):
                with open(stats_path, 'r') as f:
                    self.stats = json.load(f)
                self.logger.info("Loaded summary statistics")
            else:
                self.stats = None
                
        except Exception as e:
            self.logger.error(f"Error loading embeddings: {e}")
            raise
    
    def embed_query(self, query: str) -> np.ndarray:
        """Embed a query using the same model used for creating the index"""
        embedding = self.embedding_model.encode([query])
        return embedding.astype('float32')
    
    def retrieve_chunks(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve top-k most relevant chunks for the query
        
        Args:
            query: User query
            top_k: Number of chunks to retrieve
            
        Returns:
            List of retrieved chunks with metadata
        """
        # Embed the query
        query_embedding = self.embed_query(query)
        
        # Search in FAISS index
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Prepare results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.metadata):
                chunk_data = self.metadata[idx].copy()
                chunk_data['similarity_score'] = float(1 / (1 + distance))  # Convert distance to similarity
                chunk_data['rank'] = i + 1
                results.append(chunk_data)
        
        return results
    
    def format_context(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """Format retrieved chunks into context for the LLM"""
        context_parts = []
        
        for i, chunk in enumerate(retrieved_chunks):
            context_part = f"Document {i+1}:\n"
            
            # Add source information if available
            if 'source' in chunk:
                context_part += f"Source: {chunk['source']}\n"
            if 'source_domain' in chunk:
                context_part += f"Domain: {chunk['source_domain']}\n"
            if 'title' in chunk:
                context_part += f"Title: {chunk['title']}\n"
            
            context_part += f"Content: {chunk['chunk_text']}\n"
            context_part += f"Relevance Score: {chunk['similarity_score']:.3f}\n"
            context_part += "-" * 50 + "\n"
            
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def generate_answer_with_ollama(self, query: str, context: str) -> str:
        """Generate answer using Ollama API"""
        prompt = f"""Based on the following agricultural documents, please answer the question. Use only the information provided in the documents. If the documents don't contain enough information to answer the question, please say so.

Documents:
{context}

Question: {query}

Answer:"""

        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': self.ollama_model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.1,
                        'top_p': 0.9,
                        'num_ctx': 4096
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()['response'].strip()
            else:
                return f"Error calling Ollama API: {response.status_code} - {response.text}"
                
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to Ollama. Make sure Ollama is running on localhost:11434"
        except requests.exceptions.Timeout:
            return "Error: Request to Ollama timed out"
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def print_retrieved_chunks(self, chunks: List[Dict[str, Any]], query: str):
        """Print retrieved chunks for analysis"""
        print(f"\n{'='*80}")
        print(f"RETRIEVED CHUNKS FOR QUERY: '{query}'")
        print(f"{'='*80}")
        
        for i, chunk in enumerate(chunks):
            print(f"\n--- CHUNK {i+1} (Similarity: {chunk['similarity_score']:.3f}) ---")
            
            # Print metadata
            if 'source' in chunk:
                print(f"📄 Source: {chunk['source']}")
            if 'source_domain' in chunk:
                print(f"🏷️  Domain: {chunk['source_domain']}")
            if 'title' in chunk:
                print(f"📝 Title: {chunk['title']}")
            if 'chunk_id' in chunk:
                print(f"🆔 Chunk ID: {chunk['chunk_id']}")
            
            # Print text content
            print(f"📖 Content:")
            print(f"   {chunk['chunk_text'][:500]}{'...' if len(chunk['chunk_text']) > 500 else ''}")
            
            # Print additional metadata if available
            if 'metadata' in chunk and chunk['metadata']:
                print(f"ℹ️  Additional metadata: {chunk['metadata']}")
            
            print("-" * 60)
    
    def inspect_embeddings(self):
        """Inspect and print information about the loaded embeddings"""
        print(f"\n{'='*80}")
        print("📊 EMBEDDINGS INSPECTION")
        print(f"{'='*80}")
        
        # Basic info
        print(f"📁 Embeddings directory: {self.embeddings_dir}")
        print(f"🔢 Total vectors in FAISS index: {self.index.ntotal}")
        print(f"📄 Total metadata entries: {len(self.metadata)}")
        
        # Config info
        if hasattr(self, 'config') and self.config:
            print(f"\n⚙️  Configuration:")
            for key, value in self.config.items():
                print(f"   {key}: {value}")
        
        # Stats info
        if hasattr(self, 'stats') and self.stats:
            print(f"\n📈 Summary Statistics:")
            for key, value in self.stats.items():
                if isinstance(value, (int, float)):
                    print(f"   {key}: {value:,}")
                else:
                    print(f"   {key}: {value}")
        
        # Sample metadata entries
        print(f"\n📝 Sample metadata entries:")
        for i, entry in enumerate(self.metadata[:3]):
            print(f"\n   Entry {i+1}:")
            for key, value in entry.items():
                if key == 'chunk_text' and len(str(value)) > 100:
                    print(f"     {key}: {str(value)[:100]}...")
                else:
                    print(f"     {key}: {value}")
        
        # Available fields
        if self.metadata:
            all_fields = set()
            for entry in self.metadata:
                all_fields.update(entry.keys())
            print(f"\n🏷️  Available fields in metadata: {sorted(all_fields)}")
        
        print("=" * 80)

    def answer_query(self, query: str, top_k: int = 5, show_chunks: bool = True) -> Dict[str, Any]:
        """
        Complete RAG pipeline: retrieve chunks and generate answer
        
        Args:
            query: User question
            top_k: Number of chunks to retrieve
            show_chunks: Whether to print retrieved chunks
            
        Returns:
            Dictionary containing answer and retrieved chunks
        """
        self.logger.info(f"Processing query: {query}")
        
        # Retrieve relevant chunks
        retrieved_chunks = self.retrieve_chunks(query, top_k)
        
        if not retrieved_chunks:
            return {
                'query': query,
                'answer': "No relevant documents found for your query.",
                'retrieved_chunks': [],
                'num_chunks': 0
            }
        
        # Print chunks if requested
        if show_chunks:
            self.print_retrieved_chunks(retrieved_chunks, query)
        
        # Format context for LLM
        context = self.format_context(retrieved_chunks)
        
        # Generate answer
        print(f"\n🤔 Generating answer using {self.ollama_model}...")
        answer = self.generate_answer_with_ollama(query, context)
        
        return {
            'query': query,
            'answer': answer,
            'retrieved_chunks': retrieved_chunks,
            'num_chunks': len(retrieved_chunks)
        }

def setup_logging(debug: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def main():
    """Main function with CLI interface"""
    parser = argparse.ArgumentParser(
        description="RAG system using pre-computed embeddings and Ollama",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python rag_system.py --embeddings-dir embeddings_output
  
  # Single query
  python rag_system.py --embeddings-dir embeddings_output --query "What are the benefits of crop rotation?"
  
  # Retrieve more chunks
  python rag_system.py --embeddings-dir embeddings_output --query "Tell me about soil health" --top-k 8
  
  # Use different Ollama model
  python rag_system.py --embeddings-dir embeddings_output --ollama-model "llama3:8b"
        """
    )
    
    parser.add_argument(
        '--embeddings-dir',
        type=str,
        required=True,
        help='Directory containing saved embeddings'
    )
    
    parser.add_argument(
        '--query',
        type=str,
        default=None,
        help='Single query to process (if not provided, enters interactive mode)'
    )
    
    parser.add_argument(
        '--top-k',
        type=int,
        default=5,
        help='Number of chunks to retrieve (default: 5)'
    )
    
    parser.add_argument(
        '--ollama-model',
        type=str,
        default='gemma3:27b',
        help='Ollama model to use for generation (default: gemma3:27b)'
    )
    
    parser.add_argument(
        '--embedding-model',
        type=str,
        default='Qwen/Qwen3-Embedding-8B',
        help='Embedding model name (should match the one used for creating embeddings)'
    )
    
    parser.add_argument(
        '--no-show-chunks',
        action='store_true',
        help='Do not print retrieved chunks'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.debug)
    
    # Initialize RAG system
    try:
        print(f"🔧 Initializing RAG system...")
        print(f"📁 Embeddings directory: {args.embeddings_dir}")
        print(f"🤖 Ollama model: {args.ollama_model}")
        print(f"🧠 Embedding model: {args.embedding_model}")
        
        rag_system = RAGSystem(
            embeddings_dir=args.embeddings_dir,
            model_name=args.embedding_model,
            ollama_model=args.ollama_model
        )
        
        print("✅ RAG system initialized successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing RAG system: {e}")
        return
    
    # Process queries
    if args.query:
        # Single query mode
        result = rag_system.answer_query(
            args.query, 
            top_k=args.top_k, 
            show_chunks=not args.no_show_chunks
        )
        
        print(f"\n{'='*80}")
        print(f"FINAL ANSWER")
        print(f"{'='*80}")
        print(f"🤖 {result['answer']}")
        print(f"\n📊 Retrieved {result['num_chunks']} chunks")
        
    else:
        # Interactive mode
        print(f"\n{'='*80}")
        print("🎯 INTERACTIVE RAG SYSTEM")
        print(f"{'='*80}")
        print("Enter your questions about agriculture. Type 'quit' or 'exit' to stop.")
        print(f"Using top-{args.top_k} retrieval and {args.ollama_model} for generation.")
        print("-" * 80)
        
        while True:
            try:
                query = input("\n💭 Your question: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not query:
                    continue
                
                result = rag_system.answer_query(
                    query, 
                    top_k=args.top_k, 
                    show_chunks=not args.no_show_chunks
                )
                
                print(f"\n{'='*80}")
                print(f"ANSWER")
                print(f"{'='*80}")
                print(f"🤖 {result['answer']}")
                print(f"\n📊 Retrieved {result['num_chunks']} chunks")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error processing query: {e}")

if __name__ == "__main__":
    main()