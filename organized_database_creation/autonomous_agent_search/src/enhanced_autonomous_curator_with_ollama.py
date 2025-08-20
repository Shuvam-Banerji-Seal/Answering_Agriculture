#!/usr/bin/env python3
"""
Enhanced Autonomous Agriculture Curator with Ollama LLM Integration
Combines the autonomous search capabilities with Ollama model inference for content analysis
"""

import os
import sys
import time
import json
import logging
import requests
import threading
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import core features from the autonomous system
from autonomous_agriculture_curator import AutonomousSearchAgent, AutonomousAgricultureCurator
from agriculture_curator_fixed import (
    ImmediateJSONLWriter,
    ImprovedPDFProcessor, 
    ImprovedWebSearch,
    ExpandedAgricultureQueries,
    CurationResult
)

@dataclass
class OllamaConfig:
    """Configuration for Ollama integration"""
    base_url: str = "http://localhost:11434"
    model: str = "gemma3:1b"  # Using available model
    max_retries: int = 3
    timeout: int = 120
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 2048

class OllamaLLMProcessor:
    """Ollama LLM processor for content analysis and enhancement"""
    
    def __init__(self, config: OllamaConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        
        # Test Ollama connectivity
        self._test_connection()
        
        logging.info(f"🤖 Ollama LLM Processor initialized with model: {config.model}")
    
    def _test_connection(self) -> bool:
        """Test connection to Ollama API"""
        try:
            response = self.session.get(f"{self.config.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [model['name'] for model in models]
                logging.info(f"✅ Ollama connected. Available models: {available_models}")
                
                if self.config.model not in available_models:
                    logging.warning(f"⚠️ Model {self.config.model} not found. Using first available model.")
                    if available_models:
                        self.config.model = available_models[0]
                        logging.info(f"🔄 Switched to model: {self.config.model}")
                return True
            else:
                raise Exception(f"HTTP {response.status_code}")
        except Exception as e:
            logging.error(f"❌ Ollama connection failed: {e}")
            logging.error("Please ensure Ollama is running: ollama serve")
            return False
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response using Ollama model"""
        full_prompt = f"{prompt}\n\nContext:\n{context}" if context else prompt
        
        payload = {
            "model": self.config.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "num_predict": self.config.max_tokens
            }
        }
        
        for attempt in range(self.config.max_retries + 1):
            try:
                response = self.session.post(
                    f"{self.config.base_url}/api/generate",
                    json=payload,
                    timeout=self.config.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get('response', '').strip()
                    if content:
                        return content
                    else:
                        raise Exception("Empty response from LLM")
                else:
                    raise Exception(f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.config.max_retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logging.error(f"All {self.config.max_retries + 1} attempts failed")
                    return ""
        
        return ""
    
    def enhance_agriculture_content(self, content: str, url: str = "") -> Dict:
        """Enhance agriculture content using Ollama model"""
        prompt = """As an expert in Indian agriculture, analyze the following content and extract key information:

1. **Agricultural Domain**: Which area of agriculture does this relate to? (crops, soil, water, technology, policy, etc.)
2. **Relevance Score**: Rate relevance to Indian agriculture (0.0-1.0)
3. **Key Insights**: Extract 3-5 key insights or findings
4. **Indian Context**: How does this relate to Indian agriculture specifically?
5. **Actionable Information**: What practical applications or recommendations are mentioned?
6. **Data Points**: Extract any statistics, numbers, or quantifiable data
7. **Geographic Relevance**: Which Indian states, regions, or crops are mentioned?

Provide your analysis in JSON format with these exact keys:
{
    "domain": "string",
    "relevance_score": 0.0-1.0,
    "key_insights": ["insight1", "insight2", "insight3"],
    "indian_context": "string",
    "actionable_info": "string",
    "data_points": ["stat1", "stat2"],
    "geographic_relevance": ["state1", "region1", "crop1"]
}

Content to analyze:"""
        
        response = self.generate_response(prompt, content[:3000])  # Limit content size
        
        try:
            # Try to parse JSON response
            analysis = json.loads(response)
            
            # Validate and clean the response
            cleaned_analysis = {
                "domain": analysis.get("domain", "general"),
                "relevance_score": max(0.0, min(1.0, float(analysis.get("relevance_score", 0.5)))),
                "key_insights": analysis.get("key_insights", [])[:5],  # Limit to 5
                "indian_context": analysis.get("indian_context", ""),
                "actionable_info": analysis.get("actionable_info", ""),
                "data_points": analysis.get("data_points", [])[:10],  # Limit to 10
                "geographic_relevance": analysis.get("geographic_relevance", [])[:10],  # Limit to 10
                "llm_processed": True,
                "model_used": self.config.model,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            return cleaned_analysis
            
        except (json.JSONDecodeError, ValueError) as e:
            logging.warning(f"Failed to parse LLM response as JSON: {e}")
            # Fallback analysis
            return {
                "domain": "general",
                "relevance_score": 0.5,
                "key_insights": [],
                "indian_context": "",
                "actionable_info": "",
                "data_points": [],
                "geographic_relevance": [],
                "llm_processed": False,
                "error": str(e),
                "analysis_timestamp": datetime.now().isoformat()
            }
    
    def generate_enhanced_queries(self, specialization: str, previous_queries: List[str] = None) -> List[str]:
        """Generate enhanced search queries using Ollama model"""
        previous_context = ""
        if previous_queries:
            previous_context = f"\n\nPrevious queries used: {', '.join(previous_queries[-5:])}\nGenerate different queries to avoid repetition."
        
        prompt = f"""As an expert in {specialization} for Indian agriculture, generate 5 highly specific and effective search queries that would find the most relevant and recent information.

Focus on:
- Indian agricultural context (states, regions, crops, policies)
- Current trends and innovations
- Research publications and government reports
- Practical applications and case studies
- Data, statistics, and evidence-based information

Generate diverse queries covering different aspects of {specialization}.{previous_context}

Provide exactly 5 queries, one per line, without numbering or bullets:"""
        
        response = self.generate_response(prompt)
        
        if response:
            queries = [q.strip() for q in response.split('\n') if q.strip()]
            queries = [q for q in queries if len(q) > 10 and '?' not in q]  # Filter out questions and short queries
            return queries[:5]  # Return exactly 5 queries
        else:
            # Fallback to basic queries if LLM fails
            return [
                f"{specialization} research India",
                f"{specialization} technology Indian agriculture",
                f"{specialization} policy schemes India",
                f"{specialization} case studies India farming",
                f"{specialization} innovation trends India"
            ]

class EnhancedAutonomousAgent(AutonomousSearchAgent):
    """Enhanced autonomous agent with Ollama LLM integration"""
    
    def __init__(self, agent_id: int, specialization: str, search_engine, jsonl_writer, llm_processor: OllamaLLMProcessor):
        super().__init__(agent_id, specialization, search_engine, jsonl_writer)
        self.llm_processor = llm_processor
        self.llm_enhanced_entries = 0
        self.llm_analysis_cache = {}
        
        logging.info(f"🤖 Enhanced Agent {agent_id} ({specialization}) with LLM integration initialized")
    
    def _process_url_content_with_llm(self, url: str, content: str, metadata: Dict) -> Dict:
        """Process URL content with LLM enhancement"""
        try:
            # Get LLM analysis
            llm_analysis = self.llm_processor.enhance_agriculture_content(content, url)
            
            # Enhanced metadata with LLM insights
            enhanced_metadata = {
                **metadata,
                "llm_analysis": llm_analysis,
                "enhanced_by_llm": True,
                "content_summary": content[:500] + "..." if len(content) > 500 else content,
                "processing_timestamp": datetime.now().isoformat()
            }
            
            # Update quality score based on LLM analysis
            if llm_analysis.get("relevance_score", 0) > 0.7:
                enhanced_metadata["quality_score"] = llm_analysis["relevance_score"]
                enhanced_metadata["high_quality"] = True
            
            self.llm_enhanced_entries += 1
            return enhanced_metadata
            
        except Exception as e:
            logging.warning(f"LLM enhancement failed for {url}: {e}")
            metadata["llm_enhancement_failed"] = str(e)
            return metadata
    
    def _generate_smart_query(self) -> str:
        """Generate smart query using LLM"""
        try:
            queries = self.llm_processor.generate_enhanced_queries(
                self.specialization, 
                list(self.search_history)
            )
            
            if queries:
                selected_query = random.choice(queries)
                logging.info(f"🧠 Agent {self.agent_id} LLM-generated query: {selected_query}")
                return selected_query
            else:
                # Fallback to basic query generation
                return self._generate_basic_query()
                
        except Exception as e:
            logging.warning(f"LLM query generation failed: {e}")
            return self._generate_basic_query()
    
    def _generate_basic_query(self) -> str:
        """Generate basic query as fallback"""
        # Basic query generation logic
        areas = ["agriculture", "farming", "crops", "soil", "irrigation", "technology"]
        locations = ["India", "Punjab", "Maharashtra", "Karnataka", "Tamil Nadu"]
        
        area = random.choice(areas)
        location = random.choice(locations)
        
        return f"{area} {self.specialization} {location}"
    
    def autonomous_search_and_curate(self, num_searches: int) -> CurationResult:
        """Enhanced autonomous search with LLM integration"""
        logging.info(f"🚀 Enhanced Agent {self.agent_id} starting {num_searches} LLM-enhanced searches")
        
        start_time = time.time()
        processed_count = 0
        pdfs_processed = 0
        
        for search_num in range(num_searches):
            try:
                # Generate LLM-enhanced query
                query = self._generate_smart_query()
                
                if query in self.search_history:
                    continue  # Skip duplicates
                
                self.search_history.add(query)
                
                # Perform search
                logging.info(f"🔍 Agent {self.agent_id} search {search_num + 1}: {query}")
                search_results = self.search_engine.search_and_extract(query, self.agent_id)
                
                # Process results with LLM enhancement
                for result in search_results:
                    if result.get('url') not in self.processed_urls:
                        self.processed_urls.add(result['url'])
                        
                        # Enhanced processing with LLM
                        enhanced_result = self._process_url_content_with_llm(
                            result['url'],
                            result.get('content', ''),
                            result
                        )
                        
                        # Write to JSONL immediately
                        self.jsonl_writer.write_entry(enhanced_result)
                        processed_count += 1
                        
                        if result.get('content_type') == 'pdf':
                            pdfs_processed += 1
                        
                        # Update learning patterns
                        quality_score = enhanced_result.get('llm_analysis', {}).get('relevance_score', 0.5)
                        if quality_score > 0.7:
                            self._update_success_patterns(result, query)
                        else:
                            self._update_failure_patterns(result, query)
                
                # Brief pause between searches
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logging.error(f"Agent {self.agent_id} search failed: {e}")
                continue
        
        execution_time = time.time() - start_time
        
        result = CurationResult(
            success=True,
            agent_id=self.agent_id,
            search_query=f"Enhanced LLM autonomous curation: {num_searches} searches ({self.specialization})",
            port=0,
            processed_count=processed_count,
            pdfs_processed=pdfs_processed,
            execution_time=execution_time
        )
        
        logging.info(f"✅ Enhanced Agent {self.agent_id} completed: {processed_count} entries, {self.llm_enhanced_entries} LLM-enhanced")
        return result
    
    def _update_success_patterns(self, result: Dict, query: str):
        """Update success patterns for learning"""
        pattern = {
            'query': query,
            'url': result.get('url', ''),
            'domain': result.get('source_domain', ''),
            'content_type': result.get('content_type', ''),
            'timestamp': datetime.now().isoformat()
        }
        self.success_patterns.append(pattern)
        
        # Keep only recent patterns (last 50)
        if len(self.success_patterns) > 50:
            self.success_patterns = self.success_patterns[-50:]
    
    def _update_failure_patterns(self, result: Dict, query: str):
        """Update failure patterns to avoid in future"""
        pattern = {
            'query': query,
            'url': result.get('url', ''),
            'domain': result.get('source_domain', ''),
            'reason': 'low_quality',
            'timestamp': datetime.now().isoformat()
        }
        self.failure_patterns.append(pattern)
        
        # Keep only recent patterns (last 50)
        if len(self.failure_patterns) > 50:
            self.failure_patterns = self.failure_patterns[-50:]

class EnhancedAutonomousAgricultureCurator(AutonomousAgricultureCurator):
    """Enhanced curator with Ollama LLM integration"""
    
    def __init__(self, 
                 num_agents: int = 12,
                 output_file: str = "enhanced_autonomous_indian_agriculture.jsonl",
                 max_search_results: int = 30,
                 pdf_storage_dir: str = "enhanced_autonomous_pdfs",
                 enable_pdf_download: bool = True,
                 searches_per_agent: int = 50,
                 ollama_config: Optional[OllamaConfig] = None):
        
        # Initialize parent class
        super().__init__(num_agents, output_file, max_search_results, pdf_storage_dir, enable_pdf_download, searches_per_agent)
        
        # Initialize Ollama LLM processor
        self.ollama_config = ollama_config or OllamaConfig()
        self.llm_processor = OllamaLLMProcessor(self.ollama_config)
        
        # Enhanced analytics
        self.analytics['llm_enhanced_entries'] = 0
        self.analytics['llm_processing_time'] = 0.0
        
        logging.info("🤖 Enhanced Autonomous Agriculture Curator with Ollama LLM initialized")
        logging.info(f"🧠 Using model: {self.ollama_config.model}")
    
    def start_autonomous_curation(self) -> Dict:
        """Start enhanced autonomous curation with LLM integration"""
        logging.info("🚀 Starting ENHANCED AUTONOMOUS Agriculture Curation with Ollama LLM")
        logging.info(f"🤖 Deploying {self.num_agents} LLM-enhanced autonomous agents")
        logging.info(f"🧠 Using Ollama model: {self.ollama_config.model}")
        
        # Initialize enhanced agents with LLM
        self.agents = []
        for i in range(self.num_agents):
            specialization = self.agent_specializations[i % len(self.agent_specializations)]
            agent = EnhancedAutonomousAgent(i, specialization, self.search_engine, self.jsonl_writer, self.llm_processor)
            self.agents.append(agent)
            logging.info(f"🤖 Enhanced Agent {i}: {specialization}")
        
        # Execute enhanced autonomous curation
        logging.info("🔄 Starting parallel LLM-enhanced autonomous data curation...")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=min(self.num_agents, 4)) as executor:  # Reduced for LLM processing
            future_to_agent = {
                executor.submit(agent.autonomous_search_and_curate, self.searches_per_agent): agent 
                for agent in self.agents
            }
            
            results = []
            completed_agents = 0
            
            for future in as_completed(future_to_agent):
                agent = future_to_agent[future]
                try:
                    result = future.result()
                    results.append(result)
                    completed_agents += 1
                    
                    # Update analytics with LLM metrics
                    self._update_analytics(agent, result)
                    
                    logging.info(f"✅ Enhanced Agent {agent.agent_id} ({agent.specialization}) completed!")
                    logging.info(f"📊 Progress: {completed_agents}/{self.num_agents} agents completed")
                    logging.info(f"📝 Agent {agent.agent_id} collected: {result.processed_count} entries")
                    logging.info(f"🧠 Agent {agent.agent_id} LLM-enhanced: {result.llm_enhanced_entries} entries")
                    
                except Exception as e:
                    logging.error(f"❌ Enhanced Agent {agent.agent_id} failed: {e}")
                    completed_agents += 1
        
        execution_time = time.time() - start_time
        
        # Generate comprehensive summary with LLM metrics
        summary = self._generate_comprehensive_summary(results, execution_time)
        
        # Save detailed analytics
        self._save_detailed_analytics(summary)
        
        logging.info("🎉 ENHANCED AUTONOMOUS CURATION WITH LLM COMPLETED!")
        logging.info(f"⏱️ Total execution time: {execution_time:.2f} seconds")
        logging.info(f"📊 Total entries collected: {summary['total_entries']}")
        logging.info(f"🧠 LLM-enhanced entries: {summary['llm_enhanced_entries']}")
        logging.info(f"📁 Output file: {self.output_file}")
        
        return summary

def main():
    """Main function to run enhanced autonomous agriculture data curation with Ollama"""
    
    # Ollama configuration
    ollama_config = OllamaConfig(
        base_url="http://localhost:11434",
        model="gemma3:1b",  # Using available model
        temperature=0.7,
        max_tokens=2048
    )
    
    # Curator configuration
    config = {
        "num_agents": 8,  # Reduced for LLM processing
        "output_file": "enhanced_autonomous_indian_agriculture.jsonl",
        "max_search_results": 20,
        "pdf_storage_dir": "enhanced_autonomous_agriculture_pdfs",
        "enable_pdf_download": True,
        "searches_per_agent": 25,  # Reduced for quality over quantity
        "ollama_config": ollama_config
    }
    
    print("🌾 ENHANCED AUTONOMOUS INDIAN AGRICULTURE CURATOR WITH OLLAMA LLM 🌾")
    print(f"🤖 Model: {ollama_config.model}")
    print(f"👥 Agents: {config['num_agents']}")
    print(f"🔍 Searches per agent: {config['searches_per_agent']}")
    print(f"📁 Output: {config['output_file']}")
    print("="*80)
    
    try:
        # Initialize enhanced curator
        curator = EnhancedAutonomousAgricultureCurator(**config)
        
        # Start enhanced autonomous curation
        summary = curator.start_autonomous_curation()
        
        # Print results
        print("\n🎉 CURATION COMPLETED!")
        print(f"📊 Total entries: {summary['total_entries']}")
        print(f"🧠 LLM-enhanced entries: {summary.get('llm_enhanced_entries', 0)}")
        print(f"⏱️ Execution time: {summary['execution_time']:.2f}s")
        print(f"📁 Output file: {summary['output_file']}")
        
    except KeyboardInterrupt:
        print("\n⏹️ Curation stopped by user")
    except Exception as e:
        print(f"\n❌ Curation failed: {e}")
        logging.error(f"Main execution failed: {e}")

if __name__ == "__main__":
    main()
