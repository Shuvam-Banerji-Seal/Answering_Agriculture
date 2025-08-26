#!/usr/bin/env python3
"""
Rebuild FAISS Index to Match Embeddings
This script rebuilds the FAISS index to match the actual embeddings data.
"""

import os
import numpy as np
import faiss
import pickle
import json
import time
from pathlib import Path

def main():
    embeddings_dir = Path("/store/testing/Answering_Agriculture/agriculture_embeddings")
    
    print("🔍 Loading existing embeddings...")
    
    # Load embeddings
    embeddings_path = embeddings_dir / "embeddings.npy"
    embeddings = np.load(embeddings_path)
    print(f"📊 Loaded embeddings shape: {embeddings.shape}")
    
    # Load metadata
    metadata_pkl_path = embeddings_dir / "metadata.pkl"
    metadata_json_path = embeddings_dir / "metadata.json"
    
    if metadata_pkl_path.exists():
        with open(metadata_pkl_path, 'rb') as f:
            metadata = pickle.load(f)
        print(f"📋 Metadata entries (pickle): {len(metadata)}")
    elif metadata_json_path.exists():
        with open(metadata_json_path, 'r') as f:
            metadata = json.load(f)
        print(f"📋 Metadata entries (json): {len(metadata)}")
    else:
        print("❌ No metadata file found!")
        return
    
    # Verify dimensions
    if len(metadata) != embeddings.shape[0]:
        print(f"⚠️ Mismatch: {len(metadata)} metadata vs {embeddings.shape[0]} embeddings")
        print("🔧 Truncating to match smaller size...")
        min_size = min(len(metadata), embeddings.shape[0])
        embeddings = embeddings[:min_size]
        metadata = metadata[:min_size]
        print(f"✅ Using {min_size} entries")
    
    num_embeddings, dimension = embeddings.shape
    print(f"🎯 Building FAISS index for {num_embeddings} embeddings with {dimension} dimensions")
    
    # Ensure embeddings are float32
    if embeddings.dtype != np.float32:
        print("� Converting embeddings to float32...")
        embeddings = embeddings.astype(np.float32)
    
    # Set number of threads for CPU optimization
    num_threads = os.cpu_count()
    print(f"🔧 Using {num_threads} CPU threads")
    faiss.omp_set_num_threads(num_threads)
    
    # Choose index type based on size
    if num_embeddings > 1000000:  # 1M+
        # Use IVF for large datasets
        nlist = int(np.sqrt(num_embeddings))  # Good rule of thumb
        nlist = min(nlist, 65536)  # Cap at 64k clusters
        print(f"🎯 Using IVF with {nlist} clusters for large dataset")
        
        # Create IVF index
        quantizer = faiss.IndexFlatIP(dimension)
        index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
        
        print("🧠 Training index on CPU...")
        start_time = time.time()
        
        # Train with a subset if very large
        if num_embeddings > 5000000:
            train_size = 1000000
            train_indices = np.random.choice(num_embeddings, train_size, replace=False)
            train_data = embeddings[train_indices]
            print(f"🎲 Training with {train_size} random samples...")
        else:
            train_data = embeddings
            
        index.train(train_data)
        training_time = time.time() - start_time
        print(f"✅ Training completed in {training_time:.2f} seconds")
        
        # Add all embeddings in batches
        batch_size = 50000
        print(f"📦 Adding embeddings in batches of {batch_size}...")
        
        for i in range(0, num_embeddings, batch_size):
            end_i = min(i + batch_size, num_embeddings)
            batch = embeddings[i:end_i]
            index.add(batch)
            print(f"   Added batch {i//batch_size + 1}/{(num_embeddings + batch_size - 1)//batch_size} ({end_i}/{num_embeddings})")
            
    else:
        # Use flat index for smaller datasets
        print("� Using flat index for dataset")
        index = faiss.IndexFlatIP(dimension)
        
        print("📦 Adding all embeddings...")
        start_time = time.time()
        index.add(embeddings)
        add_time = time.time() - start_time
        print(f"✅ Added all embeddings in {add_time:.2f} seconds")
    
    print(f"📊 Index built successfully with {index.ntotal} vectors")
    
    # Save the new index
    index_path = embeddings_dir / "faiss_index.bin"
    print(f"💾 Saving FAISS index to {index_path}...")
    faiss.write_index(index, str(index_path))
    
    # Update config.json
    config_path = embeddings_dir / "config.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        config = {}
    
    config.update({
        'total_embeddings': num_embeddings,
        'dimension': dimension,
        'index_type': 'IVF' if num_embeddings > 1000000 else 'Flat',
        'rebuilt_timestamp': time.time(),
        'rebuilt_date': time.strftime('%Y-%m-%d %H:%M:%S')
    })
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Updated config.json")
    print(f"🎉 FAISS index rebuild complete!")
    print(f"📊 Final stats: {index.ntotal} vectors, {dimension}D")
    
    # Quick test
    print("🧪 Testing index with a sample query...")
    test_query = embeddings[0:1]  # Use first embedding as test
    D, I = index.search(test_query, 5)
    print(f"✅ Test successful! Found {len(I[0])} nearest neighbors")
    print(f"   Similarities: {D[0]}")
    print(f"   Indices: {I[0]}")

if __name__ == "__main__":
    main()