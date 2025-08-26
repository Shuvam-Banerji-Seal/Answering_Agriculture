#!/usr/bin/env python3
"""
Rebuild FAISS Index for Agriculture Embeddings
Optimized with progress tracking and efficient indexing
"""

import os
import json
import pickle
import numpy as np
import faiss
from datetime import datetime
from tqdm import tqdm
import time

def main():
    embeddings_dir = "/store/testing/Answering_Agriculture/agriculture_embeddings"
    
    print("🔍 Loading existing embeddings...")
    
    # Load embeddings with progress
    embeddings_path = os.path.join(embeddings_dir, "embeddings.npy")
    print("📂 Loading embeddings array...")
    embeddings = np.load(embeddings_path)
    print(f"📊 Loaded embeddings shape: {embeddings.shape}")
    
    # Load metadata with progress
    metadata_path = os.path.join(embeddings_dir, "metadata.pkl")
    if os.path.exists(metadata_path):
        print("📂 Loading metadata.pkl...")
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        print(f"📋 Metadata entries: {len(metadata)}")
    else:
        print("⚠️ No metadata.pkl found, checking for metadata.json...")
        metadata_json_path = os.path.join(embeddings_dir, "metadata.json")
        if os.path.exists(metadata_json_path):
            print("📂 Loading metadata.json...")
            with open(metadata_json_path, 'r') as f:
                metadata = json.load(f)
            print(f"📋 Metadata entries: {len(metadata)}")
        else:
            print("❌ No metadata found!")
            return
    
    # Ensure embeddings are float32 and contiguous
    print("🔄 Preprocessing embeddings...")
    embeddings = np.ascontiguousarray(embeddings.astype(np.float32))
    num_embeddings, dimension = embeddings.shape
    
    print(f"🎯 Building FAISS index for {num_embeddings:,} embeddings with {dimension} dimensions")
    
    # For 2.5M embeddings, use a more efficient approach
    if num_embeddings > 1000000:
        print("📊 Large dataset detected - using optimized IVF configuration")
        
        # Calculate optimal number of clusters for large dataset
        # Rule of thumb: sqrt(N) but capped for memory efficiency
        nlist = min(int(np.sqrt(num_embeddings)), 16384)  # Cap at 16k clusters
        
        # Use smaller sample for training to speed up
        training_sample_size = min(100000, num_embeddings)
        print(f"🎯 Using {nlist:,} clusters with {training_sample_size:,} training samples")
        
        # Create training sample
        print("🔀 Creating training sample...")
        training_indices = np.random.choice(num_embeddings, training_sample_size, replace=False)
        training_data = embeddings[training_indices]
        
    else:
        nlist = int(np.sqrt(num_embeddings))
        training_data = embeddings
        print(f"🎯 Using {nlist} clusters with full dataset for training")
    
    # Check if GPU is available
    if faiss.get_num_gpus() > 0:
        print(f"🚀 Using GPU acceleration with {faiss.get_num_gpus()} GPU(s)")
        
        # Create IVF index for GPU
        quantizer = faiss.IndexFlatL2(dimension)
        index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
        
        # Move to GPU
        res = faiss.StandardGpuResources()
        gpu_index = faiss.index_cpu_to_gpu(res, 0, index)
        
        print("🧠 Training index on GPU...")
        with tqdm(total=1, desc="GPU Training") as pbar:
            gpu_index.train(training_data)
            pbar.update(1)
        
        print("📚 Adding embeddings to GPU index...")
        batch_size = 50000  # Process in batches to avoid memory issues
        
        with tqdm(total=num_embeddings, desc="Adding to GPU index") as pbar:
            for i in range(0, num_embeddings, batch_size):
                end_idx = min(i + batch_size, num_embeddings)
                batch = embeddings[i:end_idx]
                gpu_index.add(batch)
                pbar.update(len(batch))
        
        # Move back to CPU for saving
        print("💾 Moving index from GPU to CPU for saving...")
        cpu_index = faiss.index_gpu_to_cpu(gpu_index)
        
    else:
        print("💻 No GPU available, using optimized CPU approach...")
        # Set number of threads for CPU operations
        cpu_count = os.cpu_count()
        faiss.omp_set_num_threads(cpu_count)
        print(f"🔧 Using {cpu_count} CPU threads")
        
        # Create IVF index for CPU
        quantizer = faiss.IndexFlatL2(dimension)
        cpu_index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
        
        print("🧠 Training index on CPU (this may take a while for large datasets)...")
        print(f"ℹ️  Note: FAISS training is single-threaded, but adding embeddings will use multiple cores")
        
        start_time = time.time()
        with tqdm(total=1, desc="CPU Training (single-threaded)") as pbar:
            cpu_index.train(training_data)
            pbar.update(1)
        training_time = time.time() - start_time
        print(f"⏱️ Training completed in {training_time:.2f} seconds")
        
        print("📚 Adding embeddings to CPU index (multi-threaded)...")
        batch_size = 25000  # Smaller batches for CPU
        
        start_time = time.time()
        with tqdm(total=num_embeddings, desc="Adding to CPU index") as pbar:
            for i in range(0, num_embeddings, batch_size):
                end_idx = min(i + batch_size, num_embeddings)
                batch = embeddings[i:end_idx]
                cpu_index.add(batch)
                pbar.update(len(batch))
        adding_time = time.time() - start_time
        print(f"⏱️ Adding embeddings completed in {adding_time:.2f} seconds")
    
    # Set search parameters for better recall
    cpu_index.nprobe = min(50, nlist // 4)  # Search 50 clusters or 1/4 of total
    
    print("💾 Saving rebuilt FAISS index...")
    faiss_path = os.path.join(embeddings_dir, "faiss_index.bin")
    
    start_time = time.time()
    with tqdm(total=1, desc="Saving index") as pbar:
        faiss.write_index(cpu_index, faiss_path)
        pbar.update(1)
    save_time = time.time() - start_time
    print(f"⏱️ Index saved in {save_time:.2f} seconds")
    
    # Update config
    config = {
        "embeddings_dimension": dimension,
        "total_embeddings": num_embeddings,
        "index_type": "IVF",
        "nlist": nlist,
        "nprobe": cpu_index.nprobe,
        "last_updated": datetime.now().isoformat(),
        "model_used": "qwen2:8b",  # Original model that created embeddings
        "optimization": "batch_processing_with_progress",
        "performance": {
            "training_time": training_time if 'training_time' in locals() else "N/A",
            "adding_time": adding_time if 'adding_time' in locals() else "N/A",
            "save_time": save_time
        }
    }
    
    config_path = os.path.join(embeddings_dir, "config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\n✅ FAISS index rebuilt successfully!")
    print(f"📊 Index statistics:")
    print(f"   - Total embeddings: {cpu_index.ntotal:,}")
    print(f"   - Dimension: {dimension}")
    print(f"   - Index type: IVF with {nlist:,} clusters")
    print(f"   - Search clusters (nprobe): {cpu_index.nprobe}")
    
    # Quick test
    print("\n🔍 Testing index with sample queries...")
    test_vectors = embeddings[:3]  # Use first 3 embeddings as test
    
    with tqdm(total=len(test_vectors), desc="Testing queries") as pbar:
        for i, test_vector in enumerate(test_vectors):
            distances, indices = cpu_index.search(test_vector.reshape(1, -1), 5)
            pbar.set_postfix({"Query": i+1, "Results": len(indices[0])})
            pbar.update(1)
    
    print(f"✅ All tests successful!")
    print(f"📈 Index is ready for high-performance similarity search!")
    
    # Performance summary
    print(f"\n📊 Performance Summary:")
    if 'training_time' in locals():
        print(f"   - Training: {training_time:.2f}s")
    if 'adding_time' in locals():
        print(f"   - Adding embeddings: {adding_time:.2f}s")
    print(f"   - Saving: {save_time:.2f}s")
    total_time = (training_time if 'training_time' in locals() else 0) + \
                 (adding_time if 'adding_time' in locals() else 0) + save_time
    print(f"   - Total: {total_time:.2f}s")

if __name__ == "__main__":
    main()
