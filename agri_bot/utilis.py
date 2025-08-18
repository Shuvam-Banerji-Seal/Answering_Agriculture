from prompt import prompt_gen,multi_gen
import torch
import os 
from dotenv import load_dotenv
from sarvamai import SarvamAI
import re
from IndicTransToolkit.processor import IndicProcessor


'''this speech to text was for testing model whisper '''

# def speech_to_text(audio_path,model):
#     result = model.transcribe(audio_path)
#     return result['text']

def translate_indic(model,tokenizer,text):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print('-------------------------> indic translate use horaha ')
    input_sentences=text
    tgt_lang, src_lang = "eng_Latn", "hin_Deva"
    ip = IndicProcessor(inference=True)
    batch = ip.preprocess_batch(input_sentences, src_lang=src_lang, tgt_lang=tgt_lang)

    inputs = tokenizer(
        batch,
        truncation=True,
        padding="longest",
        return_tensors="pt",
        return_attention_mask=True,
    ).to(device)
    print('-------------------------> indic translate generate ker raha  ')
    with torch.no_grad():
        generated_tokens = model.generate(
            **inputs,
            use_cache=False,
            min_length=0,
            max_length=256,
            num_beams=5,
            num_return_sequences=1,
        )
    print('-------------------------> indic translate decoding ')
    generated_tokens = tokenizer.batch_decode(
        generated_tokens,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=True,
    )
    
   
    translations = ip.postprocess_batch(generated_tokens, lang=tgt_lang)
    print('-------------------------> indic translate ne translation wapis bhej diya  ')
    print(translations)
    return translations
    
    
def speech_to_text_bharat(model,audio_path):
    model.cur_decoder = "ctc"
    lang_id='hi'
    ctc_text = model.transcribe([audio_path], batch_size=1,logprobs=False, language_id=lang_id)[0]
    return ctc_text[0]


def speech_to_text(audio_path):
    print('sarvam bhai aagaye')
    load_dotenv()
    client = SarvamAI(
        api_subscription_key= os.getenv('sarvam_api')
    )
    response = client.speech_to_text.translate(
        file=open(audio_path, "rb"),
        model="saaras:v2.5"
    )
    pattern = r"transcript='(.*?)'\s+language_code"
    match = re.search(pattern,str(response), re.DOTALL)
    transcript_text = match.group(1)
    print('sarvam bhai ne answer dediya')
    return transcript_text

def inference(model,query,device,tokenizer,retrive,max_token=500):
    ''' input as text is given apply chat template ,do retrieval then generate answer using large language model and give the output '''
    model.eval()
    with torch.inference_mode():
        print('----------------------------generate ke andar------------------------')
        print(f"------------->{query}")
        prompt=prompt_gen(query=query,tokenizer=tokenizer,data=retrive)
        print('-------------------prompt process hogaya------------------')
        print(f'----------------->{prompt}')
        input_ids = tokenizer(prompt, return_tensors="pt").to(device)
        print('-------------------genrate kar raha hai response ------------------')
        outputs = model.generate(**input_ids,
                                 temperature=0.7,
                                 do_sample=True, 
                                 max_new_tokens=max_token)
        print('-------------sarvam bhai ka response aagaya -------------------')
        output_text = tokenizer.decode(outputs[0])
        print(f'--------------{output_text}')
        text=output_text.replace(prompt, '')
        return text


def inference_multi(model,query,device,tokenizer,max_token=500):
    ''' input as text is given apply chat template ,do retrieval then generate answer using large language model and give the output '''
    model.eval()
    with torch.inference_mode():
        print('----------------------------generate ke andar------------------------')
        print(f"------------->{query}")
        prompt=multi_gen(query=query,tokenizer=tokenizer)
        print('-------------------prompt process hogaya------------------')
        print(f'----------------->{prompt}')
        input_ids = tokenizer(prompt, return_tensors="pt").to(device)
        print('-------------------genrate kar raha hai response ------------------')
        outputs = model.generate(**input_ids,
                                 temperature=0.7,
                                 do_sample=True, 
                                 max_new_tokens=max_token)
        print('-------------sarvam bhai ka response aagaya -------------------')
        output_text = tokenizer.decode(outputs[0])
        print(f'--------------{output_text}')
        text=output_text.replace(prompt, '')
        
        matches = re.findall(r"^\s*\d+\.\s+\"(.*?)\"", text, flags=re.MULTILINE)
        
        if matches:  
            data = []
            for num, m in enumerate(matches, start=1):
                data.append({f"query{num}": m})
            return data
        else: 
            return {"query1": text.strip()} 