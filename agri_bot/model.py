


import torch
import torch._dynamo as dynamo
dynamo.config.suppress_errors = True
dynamo.config.disable = True
torch._inductor.config.triton.cudagraphs = False
from transformers import AutoTokenizer, BitsAndBytesConfig, AutoModelForCausalLM
from huggingface_hub import login
import os 
from dotenv import load_dotenv


def login_in():
    load_dotenv()
    token=os.getenv('login_token')
    login(token)


# def whisper_model():
#     print('whisper model load hoaraha  ')
#     model = whisper.load_model("base")
#     print('whisper load hogaya ')
#     return model

def llm_model(quantization=False):
    device= 'cuda' if torch.cuda.is_available() else 'cpu'
    quantization_config = BitsAndBytesConfig(load_in_8bit=True)

    model_id ='google/gemma-3-1b-it'
    model=AutoModelForCausalLM.from_pretrained(pretrained_model_name_or_path=model_id,
                                               torch_dtype= torch.float16,
                                               quantization_config= quantization_config if quantization else None).to(device)
    return model, device


def model_tokenizer():
    model_id ='google/gemma-3-1b-it'
    tokenizer=AutoTokenizer.from_pretrained(pretrained_model_name_or_path=model_id)
    return tokenizer


        