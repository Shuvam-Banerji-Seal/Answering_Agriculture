#!/usr/bin/env python3
"""
Indian Agriculture Dataset BM25 RAG System
Uses BM25 with k1=0.6, b=1.0 for retrieval with proper chunking and metadata storage
"""

import json
import os
import pickle
import hashlib
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd
from tqdm import tqdm
import re
from collections import Counter, defaultdict
import math

@dataclass
class ChunkMetadata:
    """Metadata for each text chunk"""
    record_id: str
    chunk_id: int
    title: str
    author: str
    link: str
    source_domain: str
    publication_year: str
    indian_regions: List[str]
    crop_types: List[str]
    farming_methods: List[str]
    soil_types: List[str]
    climate_info: List[str]
    fertilizers: List[str]
    plant_species: List[str]
    tags: List[str]
    chunk_text: str
    chunk_start: int
    chunk_end: int
    content_length: int
    relevance_score: float

@dataclass
class SearchResult:
    """Search result with score and metadata"""
    chunk_metadata: ChunkMetadata
    bm25_score: float
    rank: int

class SimpleBM25:
    """
    BM25 implementation optimized for the agriculture dataset
    """
    
    def __init__(self, k1: float = 0.6, b: float = 1.0):
        """
        Initialize BM25 with specified parameters
        
        Args:
            k1: Controls term frequency saturation (0.6 as requested)
            b: Controls document length normalization (1.0 as requested)
        """
        self.k1 = k1
        self.b = b
        self.corpus = []
        self.doc_freqs = defaultdict(int)
        self.idf = {}
        self.doc_lens = []
        self.avgdl = 0
        self.N = 0
        
    def tokenize(self, text: str) -> List[str]:
        """Simple tokenization with agricultural term preservation"""
        if not text:
            return []
        
        # Convert to lowercase and handle basic punctuation
        text = text.lower()
        
        # Replace common punctuation with spaces, but preserve hyphens in compound words
        text = re.sub(r'[^\w\s\-]', ' ', text)
        
        # Split on whitespace and filter empty tokens
        tokens = [token.strip('-') for token in text.split() if token.strip('-')]
        
        # Remove very short tokens (less than 2 characters)
        tokens = [token for token in tokens if len(token) >= 2]
        
        return tokens
    
    def fit(self, corpus: List[str]):
        """
        Build BM25 index from corpus
        
        Args:
            corpus: List of documents (text chunks)
        """
        print("Building BM25 index...")
        self.corpus = corpus
        self.N = len(corpus)
        
        # Tokenize all documents and calculate document frequencies
        tokenized_corpus = []
        
        for doc in tqdm(corpus, desc="Tokenizing documents"):
            tokens = self.tokenize(doc)
            tokenized_corpus.append(tokens)
            self.doc_lens.append(len(tokens))
            
            # Count unique terms in this document
            unique_tokens = set(tokens)
            for token in unique_tokens:
                self.doc_freqs[token] += 1
        
        self.avgdl = sum(self.doc_lens) / len(self.doc_lens) if self.doc_lens else 0
        
        # Calculate IDF for all terms
        print("Calculating IDF scores...")
        for term, df in tqdm(self.doc_freqs.items(), desc="Computing IDF"):
            self.idf[term] = math.log((self.N - df + 0.5) / (df + 0.5) + 1.0)
        
        # Store tokenized corpus for scoring
        self.tokenized_corpus = tokenized_corpus
        
        print(f"BM25 index built: {self.N} documents, {len(self.doc_freqs)} unique terms")
        print(f"Average document length: {self.avgdl:.2f} tokens")
    
    def score_document(self, query_tokens: List[str], doc_idx: int) -> float:
        """Calculate BM25 score for a document"""
        doc_tokens = self.tokenized_corpus[doc_idx]
        doc_len = self.doc_lens[doc_idx]
        
        # Count term frequencies in document
        term_freqs = Counter(doc_tokens)
        
        score = 0.0
        for term in query_tokens:
            if term in term_freqs:
                tf = term_freqs[term]
                idf = self.idf.get(term, 0)
                
                # BM25 formula
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avgdl))
                score += idf * (numerator / denominator)
        
        return score
    
    def search(self, query: str, k: int = 10) -> List[Tuple[int, float]]:
        """
        Search for top-k most relevant documents
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of (document_index, score) tuples
        """
        query_tokens = self.tokenize(query)
        if not query_tokens:
            return []
        
        scores = []
        for doc_idx in range(self.N):
            score = self.score_document(query_tokens, doc_idx)
            if score > 0:  # Only include documents with positive scores
                scores.append((doc_idx, score))
        
        # Sort by score (descending) and return top-k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:k]

class AgricultureBM25System:
    """Main BM25 RAG system for agriculture dataset"""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Initialize the BM25 system
        
        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.bm25 = SimpleBM25(k1=0.6, b=1.0)  # Parameters as requested
        self.chunks = []
        self.metadata = []
        
    def chunk_text(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of (chunk_text, start_pos, end_pos) tuples
        """
        if not text or len(text.strip()) == 0:
            return []
        
        text = text.strip()
        if len(text) <= self.chunk_size:
            return [(text, 0, len(text))]
        
        chunks = []
        start_idx = 0
        
        while start_idx < len(text):
            end_idx = min(start_idx + self.chunk_size, len(text))
            
            # Try to break at sentence boundaries
            chunk_text = text[start_idx:end_idx]
            
            # If this isn't the last chunk, try to find a good breaking point
            if end_idx < len(text):
                # Look for sentence endings near the end of the chunk
                for i in range(len(chunk_text) - 1, max(0, len(chunk_text) - 100), -1):
                    if chunk_text[i] in '.!?':
                        chunk_text = chunk_text[:i + 1]
                        end_idx = start_idx + i + 1
                        break
                # If no sentence boundary found, look for word boundaries
                else:
                    for i in range(len(chunk_text) - 1, max(0, len(chunk_text) - 50), -1):
                        if chunk_text[i].isspace():
                            chunk_text = chunk_text[:i]
                            end_idx = start_idx + i
                            break
            
            if chunk_text.strip():
                chunks.append((chunk_text.strip(), start_idx, end_idx))
            
            # Move start position with overlap
            start_idx = max(start_idx + 1, end_idx - self.chunk_overlap)
            if start_idx >= len(text):
                break
                
        return chunks
    
    def process_record(self, record: Dict[str, Any], record_idx: int) -> List[ChunkMetadata]:
        """Process a single JSONL record into chunks"""
        # Extract main text content
        main_text = ""
        if record.get('text_extracted'):
            main_text += record['text_extracted'] + " "
        if record.get('abstract'):
            main_text += record['abstract'] + " "
        
        if not main_text.strip():
            return []
        
        # Create unique record ID
        record_id = hashlib.md5(f"{record.get('link', '')}{record_idx}".encode()).hexdigest()
        
        # Chunk the text
        chunks = self.chunk_text(main_text.strip())
        
        chunk_metadata_list = []
        
        for chunk_idx, (chunk_text, start_pos, end_pos) in enumerate(chunks):
            if len(chunk_text.strip()) < 50:  # Skip very short chunks
                continue
            
            # Create metadata
            metadata = ChunkMetadata(
                record_id=record_id,
                chunk_id=chunk_idx,
                title=record.get('title', ''),
                author=record.get('author', ''),
                link=record.get('link', ''),
                source_domain=record.get('source_domain', ''),
                publication_year=record.get('publication_year', ''),
                indian_regions=record.get('indian_regions', []),
                crop_types=record.get('crop_types', []),
                farming_methods=record.get('farming_methods', []),
                soil_types=record.get('soil_types', []),
                climate_info=record.get('climate_info', []),
                fertilizers=record.get('fertilizers', []),
                plant_species=record.get('plant_species', []),
                tags=record.get('tags', []),
                chunk_text=chunk_text,
                chunk_start=start_pos,
                chunk_end=end_pos,
                content_length=len(chunk_text),
                relevance_score=record.get('relevance_score', 1.0)
            )
            
            chunk_metadata_list.append(metadata)
            self.metadata.append(metadata)
            self.chunks.append(chunk_text)
            
        return chunk_metadata_list
    
    def process_dataset(self, jsonl_file: str, max_records: Optional[int] = None):
        """Process the entire JSONL dataset"""
        if not os.path.exists(jsonl_file):
            raise FileNotFoundError(f"Dataset file not found: {jsonl_file}")
        
        print(f"Processing dataset: {jsonl_file}")
        
        total_records = 0
        processed_records = 0
        total_chunks = 0
        
        # Count total records first
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    total_records += 1
        
        print(f"Total records in dataset: {total_records}")
        
        if max_records:
            total_records = min(total_records, max_records)
            print(f"Processing first {total_records} records")
        
        # Process records
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            pbar = tqdm(total=total_records, desc="Processing records")
            
            for record_idx, line in enumerate(f):
                if max_records and processed_records >= max_records:
                    break
                    
                if not line.strip():
                    continue
                
                try:
                    record = json.loads(line)
                    chunks = self.process_record(record, record_idx)
                    total_chunks += len(chunks)
                    processed_records += 1
                    
                    pbar.set_postfix({
                        'chunks': total_chunks,
                        'avg_chunks_per_record': f"{total_chunks/processed_records:.1f}"
                    })
                    pbar.update(1)
                    
                except json.JSONDecodeError as e:
                    print(f"Error parsing line {record_idx}: {e}")
                    continue
                except Exception as e:
                    print(f"Error processing record {record_idx}: {e}")
                    continue
            
            pbar.close()
        
        print(f"Processed {processed_records} records into {total_chunks} chunks")
        return processed_records, total_chunks
    
    def build_index(self):
        """Build BM25 index from processed chunks"""
        if not self.chunks:
            raise ValueError("No chunks to index")
        
        print("Building BM25 index with parameters: k1=0.6, b=1.0")
        self.bm25.fit(self.chunks)
    
    def search(self, query: str, k: int = 10) -> List[SearchResult]:
        """
        Search for relevant chunks
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of SearchResult objects with metadata and scores
        """
        if not self.bm25.corpus:
            raise ValueError("BM25 index not built. Call build_index() first.")
        
        # Get BM25 scores
        results = self.bm25.search(query, k)
        
        # Convert to SearchResult objects
        search_results = []
        for rank, (doc_idx, score) in enumerate(results):
            search_result = SearchResult(
                chunk_metadata=self.metadata[doc_idx],
                bm25_score=score,
                rank=rank + 1
            )
            search_results.append(search_result)
        
        return search_results
    
    def save_index(self, output_dir: str = "bm25_index"):
        """Save BM25 index and metadata to disk"""
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Saving BM25 index to {output_dir}/...")
        
        # Save BM25 model
        bm25_data = {
            'k1': self.bm25.k1,
            'b': self.bm25.b,
            'corpus': self.bm25.corpus,
            'doc_freqs': dict(self.bm25.doc_freqs),
            'idf': self.bm25.idf,
            'doc_lens': self.bm25.doc_lens,
            'avgdl': self.bm25.avgdl,
            'N': self.bm25.N,
            'tokenized_corpus': self.bm25.tokenized_corpus
        }
        
        with open(os.path.join(output_dir, "bm25_index.pkl"), 'wb') as f:
            pickle.dump(bm25_data, f)
        
        # Save metadata
        metadata_dicts = []
        for meta in self.metadata:
            metadata_dicts.append(asdict(meta))
        
        with open(os.path.join(output_dir, "metadata.json"), 'w', encoding='utf-8') as f:
            json.dump(metadata_dicts, f, ensure_ascii=False, indent=2)
        
        # Save as pickle for faster loading
        with open(os.path.join(output_dir, "metadata.pkl"), 'wb') as f:
            pickle.dump(self.metadata, f)
        
        # Save chunks
        with open(os.path.join(output_dir, "chunks.json"), 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=2)
        
        # Save configuration
        config = {
            'bm25_k1': self.bm25.k1,
            'bm25_b': self.bm25.b,
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'total_chunks': len(self.chunks),
            'total_documents': self.bm25.N,
            'avg_document_length': self.bm25.avgdl,
            'vocabulary_size': len(self.bm25.doc_freqs)
        }
        
        with open(os.path.join(output_dir, "config.json"), 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"Saved BM25 index with {len(self.chunks)} chunks")
        
        # Create summary statistics
        self.create_summary_stats(output_dir)
    
    def load_index(self, index_dir: str = "bm25_index"):
        """Load BM25 index and metadata from disk"""
        print(f"Loading BM25 index from {index_dir}/...")
        
        # Load BM25 model
        with open(os.path.join(index_dir, "bm25_index.pkl"), 'rb') as f:
            bm25_data = pickle.load(f)
        
        self.bm25.k1 = bm25_data['k1']
        self.bm25.b = bm25_data['b']
        self.bm25.corpus = bm25_data['corpus']
        self.bm25.doc_freqs = defaultdict(int, bm25_data['doc_freqs'])
        self.bm25.idf = bm25_data['idf']
        self.bm25.doc_lens = bm25_data['doc_lens']
        self.bm25.avgdl = bm25_data['avgdl']
        self.bm25.N = bm25_data['N']
        self.bm25.tokenized_corpus = bm25_data['tokenized_corpus']
        
        # Load metadata
        with open(os.path.join(index_dir, "metadata.pkl"), 'rb') as f:
            self.metadata = pickle.load(f)
        
        # Load chunks
        with open(os.path.join(index_dir, "chunks.json"), 'r', encoding='utf-8') as f:
            self.chunks = json.load(f)
        
        print(f"Loaded BM25 index with {len(self.chunks)} chunks")
    
    def create_summary_stats(self, output_dir: str):
        """Create summary statistics about the dataset"""
        if not self.metadata:
            return
        
        stats = {
            'total_chunks': len(self.metadata),
            'unique_records': len(set(meta.record_id for meta in self.metadata)),
            'avg_chunk_length': np.mean([meta.content_length for meta in self.metadata]),
            'total_content_length': sum(meta.content_length for meta in self.metadata),
            'bm25_parameters': {
                'k1': self.bm25.k1,
                'b': self.bm25.b,
                'vocabulary_size': len(self.bm25.doc_freqs),
                'avg_document_length': self.bm25.avgdl
            },
            'source_domains': {},
            'crop_types': {},
            'farming_methods': {},
            'soil_types': {},
            'climate_info': {},
            'fertilizers': {},
            'tags': {}
        }
        
        # Count occurrences
        for meta in self.metadata:
            # Source domains
            domain = meta.source_domain
            stats['source_domains'][domain] = stats['source_domains'].get(domain, 0) + 1
            
            # Agricultural categories
            for crop in meta.crop_types:
                stats['crop_types'][crop] = stats['crop_types'].get(crop, 0) + 1
            
            for method in meta.farming_methods:
                stats['farming_methods'][method] = stats['farming_methods'].get(method, 0) + 1
            
            for soil in meta.soil_types:
                stats['soil_types'][soil] = stats['soil_types'].get(soil, 0) + 1
            
            for climate in meta.climate_info:
                stats['climate_info'][climate] = stats['climate_info'].get(climate, 0) + 1
            
            for fertilizer in meta.fertilizers:
                stats['fertilizers'][fertilizer] = stats['fertilizers'].get(fertilizer, 0) + 1
            
            for tag in meta.tags:
                stats['tags'][tag] = stats['tags'].get(tag, 0) + 1
        
        # Sort by frequency
        for key in ['source_domains', 'crop_types', 'farming_methods', 'soil_types', 
                   'climate_info', 'fertilizers', 'tags']:
            stats[key] = dict(sorted(stats[key].items(), key=lambda x: x[1], reverse=True))
        
        with open(os.path.join(output_dir, "summary_stats.json"), 'w') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"Created summary statistics in {output_dir}/summary_stats.json")

def main():
    """Main function to create BM25 index"""
    # Configuration
    JSONL_FILE = "../autonomous_indian_agriculture_complete.jsonl"
    OUTPUT_DIR = "agriculture_bm25_index"
    MAX_RECORDS = None  # Process all records
    
    print("Creating BM25 RAG system for Indian Agriculture Dataset")
    print("Parameters: k1=0.6, b=1.0")
    
    # Initialize BM25 system
    bm25_system = AgricultureBM25System(
        chunk_size=512,
        chunk_overlap=50
    )
    
    # Process dataset
    try:
        processed_records, total_chunks = bm25_system.process_dataset(
            JSONL_FILE, max_records=MAX_RECORDS
        )
        
        if total_chunks == 0:
            print("No chunks created. Exiting.")
            return
        
        # Build BM25 index
        bm25_system.build_index()
        
        # Save index
        bm25_system.save_index(OUTPUT_DIR)
        
        print(f"\nBM25 index creation completed!")
        print(f"- Processed {processed_records} records")
        print(f"- Created {total_chunks} text chunks")
        print(f"- Saved to {OUTPUT_DIR}/")
        print(f"- BM25 parameters: k1=0.6, b=1.0")
        print(f"- Index ready for retrieval with inline citations")
        
        # Example search to test the system
        print("\n" + "="*50)
        print("Testing search functionality...")
        
        test_queries = [
            "rice cultivation methods",
            "organic farming techniques",
            "soil fertility management",
            "crop rotation benefits"
        ]
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            results = bm25_system.search(query, k=3)
            
            if results:
                print("Top 3 results:")
                for result in results:
                    print(f"  Rank {result.rank}: Score {result.bm25_score:.4f}")
                    print(f"    Title: {result.chunk_metadata.title[:80]}...")
                    print(f"    Source: {result.chunk_metadata.source_domain}")
                    print(f"    Content: {result.chunk_metadata.chunk_text[:100]}...")
                    print()
            else:
                print("  No results found")
        
    except FileNotFoundError:
        print(f"Error: Dataset file '{JSONL_FILE}' not found!")
        print("Please ensure the JSONL file is in the current directory.")
    except Exception as e:
        print(f"Error during processing: {e}")
        raise

if __name__ == "__main__":
    main()
