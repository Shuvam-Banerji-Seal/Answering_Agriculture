
''' prompt ke make sure kar ki agri bot me jo tokenizer liya hai usko  prompt ke time send kar kar raha '''

def prompt_gen(query:str,tokenizer,data):
    base_prompt=f""" 

You are KrishiMitra (Farm Friend), an AI-powered agricultural advisor designed to serve the diverse needs of India's agricultural ecosystem. 
You are a trusted, knowledgeable companion who understands the complexities of Indian agriculture and can provide practical, actionable
guidance to farmers, financiers, vendors, and all stakeholders in the agricultural value chain.

this is the data-:{data}

follwing is my query respond accordingly-:{query}
"""
    dialogue_template = [
            {"role": "user",
            "content": base_prompt}
        ]
    prompt = tokenizer.apply_chat_template(conversation=dialogue_template,
                                          tokenize=False
                                          ,add_generation_prompt=True)
    return prompt


def multi_gen(query:str,tokenizer):
    base_prompt=f""" 
You are a query expansion specialist for a retrieval system. Your task is to generate multiple search variations of the original query to maximize retrieval of relevant documents.

**Original Query:** "{query}"

Generate exactly 5 expanded queries following these guidelines:

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

**Output Format:**
1. [Synonym variation]
2. [Technical version]
3. [Simplified version]  
4. [Context expanded]
5. [Perspective shifted]

    
"""
    dialogue_template = [
            {"role": "user",
            "content": base_prompt}
        ]
    prompt = tokenizer.apply_chat_template(conversation=dialogue_template,
                                          tokenize=False,
                                          add_generation_prompt=True)
    return prompt