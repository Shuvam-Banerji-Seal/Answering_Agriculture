


import torch
import torch._dynamo as dynamo
dynamo.config.suppress_errors = True
dynamo.config.disable = True
torch._inductor.config.triton.cudagraphs = False
import nemo.collections.asr as nemo_asr
from transformers import AutoTokenizer, BitsAndBytesConfig, AutoModelForCausalLM
from huggingface_hub import login
import os 
from dotenv import load_dotenv
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from huggingface_hub import login
import torch 
from IndicTransToolkit.processor import IndicProcessor

def login_in():
    load_dotenv()
    token=os.getenv('login_token')
    login(token)

def  load_indic_trans():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_name = "ai4bharat/indictrans2-indic-en-dist-200M"
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    
    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_name, 
        trust_remote_code=True, 
        torch_dtype=torch.float16, 
        attn_implementation="flash_attention_2"
    ).to(device)
    
    return model, tokenizer

    
def ai_bharat():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_path='conformer.nemo'
    model = nemo_asr.models.EncDecCTCModel.restore_from(restore_path=model_path)
    model.eval() 
    model = model.to(device)
    return model


    
def whisper_model():
    print('whisper model load hoaraha  ')
    model = whisper.load_model("base")
    print('whisper load hogaya ')
    return model

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


        