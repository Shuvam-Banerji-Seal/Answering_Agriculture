import torch
import os 
# from dotenv import load_dotenv
from sarvamai import SarvamAI
import re
# from IndicTransToolkit.processor import IndicProcessor
import subprocess

def speech_to_text_bharat(model,audio_path):
    model.cur_decoder = "ctc"
    lang_id='hi'
    ctc_text = model.transcribe([audio_path], batch_size=1,logprobs=False, language_id=lang_id)[0]
    return ctc_text[0]


def translate_indic(model,tokenizer,text,audio_code):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    input_sentences=text
    tgt_lang, src_lang = "eng_Latn", 'mar_Deva'
    ip = IndicProcessor(inference=True)
    batch = ip.preprocess_batch(input_sentences, src_lang=src_lang, tgt_lang=tgt_lang)

    inputs = tokenizer(
        batch,
        truncation=True,
        padding="longest",
        return_tensors="pt",
        return_attention_mask=True,
    ).to(device)
    with torch.no_grad():
        generated_tokens = model.generate(
            **inputs,
            use_cache=False,
            min_length=0,
            max_length=256,
            num_beams=5,
            num_return_sequences=1,
        )
    generated_tokens = tokenizer.batch_decode(
        generated_tokens,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=True,
    )
    
   
    translations = ip.postprocess_batch(generated_tokens, lang=tgt_lang)
    return translations


def mono_channel(audio_loc):
    mono_path=audio_loc
    web_audio_path = "temp_audio_mono.wav"
    command = ["ffmpeg", "-y", "-i", mono_path, "-ac", "1", "-ar", "16000", web_audio_path]
    subprocess.run(command, check=True)
    return web_audio_path

def text_to_text(text:str,sarvam_api,src_lan,tg_lan="en-IN"):
    # load_dotenv()
    client = SarvamAI(
        api_subscription_key= sarvam_api
    )
    response = client.text.translate(
    input=text,
    source_language_code=src_lan,  
    target_language_code=tg_lan,
    model="sarvam-translate:v1"
)
    pattern = r"translated_text='(.*?)'\s+source_language_code"
    match = re.search(pattern,str(response), re.DOTALL)
    translated_text = match.group(1)
    return translated_text


def speech_to_text(audio_path,sarvam_api):
    # load_dotenv()
    client = SarvamAI(
        api_subscription_key= sarvam_api
    )
    response = client.speech_to_text.translate(
        file=open(audio_path, "rb"),
        model="saaras:v2.5"
    )
    pattern = r"transcript='(.*?)'\s+language_code"
    match = re.search(pattern,str(response), re.DOTALL)
    transcript_text = match.group(1)
    return transcript_text

    