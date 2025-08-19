
from utility import speech_to_text_bharat, translate_indic ,mono_channel,speech_to_text
import os
from load import login_in ,ai_bharat ,load_indic_trans
from huggingface_hub import login


def ai_bharat_load():
    ai_b=ai_bharat()
    return ai_b


def indic_load():
    sl,tl=load_indic_trans()
    return sl,tl


def main(audio_path='marathi01.wav',audio_code='mar_Deva',loaded_model=True,api_key=None,hugging_token=None):
    login(hugging_token)
    web_audio_path=mono_channel(audio_loc=audio_path)
    if not audio_code:
        audio_code='hin_Deva'
    if loaded_model:
        ai_bha=ai_bharat_load()
        indic_mod,indic_tok=indic_load()
        text=speech_to_text_bharat(model=ai_bha,audio_path=web_audio_path)
        transcript=translate_indic(model=indic_mod,tokenizer=indic_tok,text=[text],audio_code=audio_code)[0]
    else:
        transcript=speech_to_text(audio_path=web_audio_path,sarvam_api=api_key)
    os.remove(web_audio_path)
    return transcript



        