"""
Base classes and interfaces for sub-query generation.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass
import logging


@dataclass
class SubQueryResult:
    """Container for sub-query generation results."""
    original_query: str
    sub_queries: List[str]
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            'original_query': self.original_query,
            'sub_queries': self.sub_queries,
            'metadata': self.metadata or {}
        }


class SubQueryGenerator(ABC):
    """Abstract base class for sub-query generators."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def generate_sub_queries(self, query: str) -> SubQueryResult:
        """
        Generate sub-queries from the original query.
        
        Args:
            query: Original query string
            
        Returns:
            SubQueryResult containing the original query and generated sub-queries
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the generator is available and properly configured."""
        pass
    
    def _create_prompt(self, query: str) -> str:
        """Create the prompt for sub-query generation."""
        num_queries = self.config.get('generation', {}).get('num_sub_queries', 5)
        
        prompt = f"""You are a query expansion specialist for a retrieval system. Your task is to generate multiple search variations of the original query to maximize retrieval of relevant documents.

**Original Query:** "{query}"

Generate exactly {num_queries} expanded queries following these guidelines:

1. **Synonym Variation**: Replace key terms with synonyms and alternative phrasings
2. **Technical Reformulation**: Use domain-specific terminology and technical language
3. **Simplified Version**: Rephrase using common, everyday language
4. **Context Expansion**: Add implicit context or background information that might be relevant
5. **Perspective Shift**: Approach the same information need from a different angle or use case

**Requirements:**
- Keep the core intent and meaning unchanged
- Each variation should be 1-2 sentences maximum
- Focus on terms that would appear in relevant documents
- Avoid redundant variations
- Prioritize searchable keywords over conversational language
- Format each query as a complete sentence that could appear in an article

**Output Format:**
1. [First variation]
2. [Second variation]
3. [Third variation]
4. [Fourth variation]
5. [Fifth variation]

Only return the numbered list of queries, nothing else."""

        return prompt
    
    def _parse_response(self, response: str) -> List[str]:
        """Parse the model response to extract sub-queries."""
        import re
        
        # Try to extract numbered queries
        patterns = [
            r'^\s*\d+\.\s*"([^"]+)"',  # Quoted format
            r'^\s*\d+\.\s*([^\n]+)',   # Simple numbered format
            r'^\s*\d+\)\s*([^\n]+)',   # Parentheses format
        ]
        
        queries = []
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    query = match.group(1).strip()
                    # Clean up the query
                    query = query.strip('"\'.,')
                    if query and len(query) > 10:  # Minimum length check
                        queries.append(query)
                    break
        
        # If no numbered format found, try to split by lines
        if not queries:
            for line in lines:
                line = line.strip()
                if line and len(line) > 10 and not line.startswith(('**', '#', 'Original')):
                    queries.append(line.strip('"\'.,'))
        
        return queries[:self.config.get('generation', {}).get('num_sub_queries', 5)]