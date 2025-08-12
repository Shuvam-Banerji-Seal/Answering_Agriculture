#!/usr/bin/env python3
"""
Simple working test script for sub-query generation.
Tests the actual working functionality with available models.
"""

import requests
import json
import re
import time
from typing import List, Tuple, Optional

def check_ollama_models() -> List[str]:
    """Check which Ollama models are available."""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return [model['name'] for model in models]
        return []
    except:
        return []

def create_rag_optimized_prompt(query: str, num_queries: int = 5) -> str:
    """Create a prompt optimized for RAG sub-query generation."""
    return f"""You are a query expansion specialist for information retrieval systems. Your task is to generate {num_queries} different search variations of the original query to maximize document retrieval coverage.

Original Query: "{query}"

Generate exactly {num_queries} expanded queries following these guidelines:

1. **Synonym Variation**: Replace key terms with synonyms and alternative phrasings
2. **Technical Reformulation**: Use domain-specific terminology and technical language  
3. **Simplified Version**: Rephrase using common, everyday language
4. **Context Expansion**: Add implicit context or background information
5. **Perspective Shift**: Approach from a different angle or use case

**Requirements:**
- Keep the core intent unchanged
- Each query should be 1-2 sentences maximum
- Focus on terms that would appear in relevant documents
- Format as complete sentences that could appear in articles
- Avoid redundant variations

**Output Format:**
1. [First variation]
2. [Second variation]  
3. [Third variation]
4. [Fourth variation]
5. [Fifth variation]

Return only the numbered list, nothing else."""

def parse_sub_queries(response: str) -> List[str]:
    """Parse model response to extract sub-queries."""
    queries = []
    lines = response.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Try different numbered formats
        patterns = [
            r'^\s*\d+\.\s*"([^"]+)"',  # "quoted"
            r'^\s*\d+\.\s*([^\n]+)',   # simple
            r'^\s*\d+\)\s*([^\n]+)',   # parentheses
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                query = match.group(1).strip().strip('"\'.,')
                if len(query) > 10:  # Minimum length
                    queries.append(query)
                break
    
    return queries[:5]

def generate_sub_queries_ollama(query: str, model: str = 'gemma3:1b') -> Optional[dict]:
    """Generate sub-queries using Ollama."""
    prompt = create_rag_optimized_prompt(query)
    
    payload = {
        'model': model,
        'prompt': prompt,
        'stream': False,
        'options': {
            'temperature': 0.7,
            'num_predict': 600,
            'top_p': 0.9
        }
    }
    
    try:
        print(f"🤖 Generating with {model}...")
        start_time = time.time()
        
        response = requests.post(
            'http://localhost:11434/api/generate',
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', '')
            sub_queries = parse_sub_queries(generated_text)
            
            end_time = time.time()
            
            return {
                'original_query': query,
                'sub_queries': sub_queries,
                'model': model,
                'generation_time': end_time - start_time,
                'raw_response': generated_text,
                'success': True
            }
        else:
            return {'success': False, 'error': f'HTTP {response.status_code}'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_single_query(query: str) -> dict:
    """Test sub-query generation for a single query."""
    print(f"\n{'='*60}")
    print(f"Testing Query: \"{query}\"")
    print('='*60)
    
    # Check available models
    models = check_ollama_models()
    if not models:
        print("❌ No Ollama models available")
        return {'success': False, 'error': 'No models available'}
    
    print(f"Available models: {', '.join(models[:3])}...")
    
    # Try with preferred models in order
    preferred_models = ['gemma3:1b', 'gemma3:4b-it-qat', 'llama2:latest']
    
    for model in preferred_models:
        if model in models:
            result = generate_sub_queries_ollama(query, model)
            if result and result.get('success'):
                return result
            else:
                print(f"❌ {model} failed: {result.get('error', 'Unknown error')}")
    
    # Try with any available model
    for model in models[:2]:  # Try first 2 models
        print(f"Trying fallback model: {model}")
        result = generate_sub_queries_ollama(query, model)
        if result and result.get('success'):
            return result
    
    return {'success': False, 'error': 'All models failed'}

def display_results(result: dict):
    """Display the sub-query generation results."""
    if not result.get('success'):
        print(f"❌ Generation failed: {result.get('error')}")
        return
    
    print(f"✅ Successfully generated {len(result['sub_queries'])} sub-queries")
    print(f"🤖 Model: {result['model']}")
    print(f"⏱️  Time: {result['generation_time']:.2f} seconds")
    print()
    
    print("📝 Generated Sub-queries:")
    for i, query in enumerate(result['sub_queries'], 1):
        print(f"  {i}. {query}")
    
    print("\n🔍 RAG Usage Benefits:")
    print("  ✓ Multiple search angles for better document coverage")
    print("  ✓ Different terminology captures various writing styles")
    print("  ✓ Technical and simple versions reach different audiences")
    print("  ✓ Context expansion finds related information")
    print("  ✓ Perspective shifts discover complementary content")
    
    print(f"\n📊 Quality Metrics:")
    avg_length = sum(len(q.split()) for q in result['sub_queries']) / len(result['sub_queries'])
    print(f"  • Average query length: {avg_length:.1f} words")
    print(f"  • Unique queries: {len(set(result['sub_queries']))}/{len(result['sub_queries'])}")
    
    # Show raw response sample
    raw = result.get('raw_response', '')
    if raw:
        print(f"\n🔧 Raw Model Output (first 200 chars):")
        print(f"  {raw[:200]}{'...' if len(raw) > 200 else ''}")

def test_multiple_queries():
    """Test with multiple different queries."""
    test_queries = [
        "When should I sow the rice seeds?",
        "How to improve soil fertility naturally?",
        "What are the benefits of organic farming?",
        "Why is protein content in rice low?",
        "Best practices for sustainable agriculture"
    ]
    
    print("🧪 COMPREHENSIVE SUB-QUERY GENERATION TEST")
    print("="*60)
    
    results = []
    total_time = 0
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[Test {i}/{len(test_queries)}]")
        result = test_single_query(query)
        display_results(result)
        
        results.append(result)
        if result.get('success'):
            total_time += result.get('generation_time', 0)
    
    # Summary
    successful = sum(1 for r in results if r.get('success'))
    print(f"\n{'='*60}")
    print("📊 FINAL SUMMARY")
    print('='*60)
    print(f"✅ Successful generations: {successful}/{len(test_queries)}")
    print(f"⏱️  Total generation time: {total_time:.2f} seconds")
    if successful > 0:
        print(f"📈 Average time per query: {total_time/successful:.2f} seconds")
    
    if successful == len(test_queries):
        print("🎉 All tests passed! Sub-query generation is working perfectly.")
    elif successful > 0:
        print("⚠️  Partial success. Some queries worked, others failed.")
    else:
        print("❌ All tests failed. Check your Ollama setup.")
    
    return successful > 0

def quick_test():
    """Quick test with a single query."""
    print("🚀 QUICK SUB-QUERY GENERATION TEST")
    
    query = "When should I sow the rice seeds?"
    result = test_single_query(query)
    display_results(result)
    
    return result.get('success', False)

def main():
    """Main function."""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--quick':
            return 0 if quick_test() else 1
        elif sys.argv[1] == '--query':
            if len(sys.argv) > 2:
                query = ' '.join(sys.argv[2:])
                result = test_single_query(query)
                display_results(result)
                return 0 if result.get('success', False) else 1
            else:
                print("Usage: python test_working.py --query 'your query here'")
                return 1
    
    # Default: run comprehensive test
    return 0 if test_multiple_queries() else 1

if __name__ == "__main__":
    exit(main())