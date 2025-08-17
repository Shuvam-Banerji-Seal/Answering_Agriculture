
''' prompt ke make sure kar ki agri bot me jo tokenizer liya hai usko  prompt ke time send kar kar raha '''

def prompt_gen(query:str,tokenizer):
    base_prompt=f""" 

You are KrishiMitra (Farm Friend), an AI-powered agricultural advisor designed to serve the diverse needs of India's agricultural ecosystem. 
You are a trusted, knowledgeable companion who understands the complexities of Indian agriculture and can provide practical, actionable
guidance to farmers, financiers, vendors, and all stakeholders in the agricultural value chain.

here is query response accodingly-:{query}
"""
    dialogue_template = [
            {"role": "user",
            "content": base_prompt}
        ]
    prompt = tokenizer.apply_chat_template(conversation=dialogue_template,
                                          tokenize=False
                                          ,add_generation_prompt=True)
    return prompt