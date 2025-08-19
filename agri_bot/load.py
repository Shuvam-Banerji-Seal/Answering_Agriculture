import torch
import torch._dynamo as dynamo
dynamo.config.suppress_errors = True
dynamo.config.disable = True
torch._inductor.config.triton.cudagraphs = False
import nemo.collections.asr as nemo_asr
from transformers import AutoTokenizer, BitsAndBytesConfig, AutoModelForCausalLM

import os 
from dotenv import load_dotenv
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from IndicTransToolkit.processor import IndicProcessor
import subprocess



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
