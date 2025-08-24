
from utility import speech_to_text_bharat, translate_indic ,mono_channel,speech_to_text,text_to_text
import os
from load import ai_bharat ,load_indic_trans
from huggingface_hub import login


def ai_bharat_load():
    ai_b=ai_bharat()
    return ai_b


def indic_load():
    sl,tl=load_indic_trans()
    return sl,tl

sarvam_lang_codes = {
    "Assamese": "as-IN",
    "Bengali": "bn-IN",
    "Bodo": "brx-IN",
    "Dogri": "doi-IN",
    "English": "en-IN",
    "Gujarati": "gu-IN",
    "Hindi": "hi-IN",
    "Kannada": "kn-IN",
    "Kashmiri": "ks-IN",
    "Konkani": "kok-IN",
    "Maithili": "mai-IN",
    "Malayalam": "ml-IN",
    "Manipuri": "mni-IN",
    "Marathi": "mr-IN",
    "Nepali": "ne-IN",
    "Odia": "od-IN",
    "Punjabi": "pa-IN",
    "Sanskrit": "sa-IN",
    "Santali": "sat-IN",
    "Sindhi": "sd-IN",
    "Tamil": "ta-IN",
    "Telugu": "te-IN",
    "Urdu": "ur-IN",
}

api_key=""
token=""

def main(audio_path='marathi01.wav',audio_code='mar_Deva',loaded_model=False,api_key=api_key,hugging_token=token):
    login(hugging_token)
    web_audio_path=mono_channel(audio_loc=audio_path)
    if not audio_code:
        print('audio code me huu')
        audio_code='hin_Deva'
    if loaded_model:
        ai_bha=ai_bharat_load()
        indic_mod,indic_tok=indic_load()
        text=speech_to_text_bharat(model=ai_bha,audio_path=web_audio_path)
        transcript=translate_indic(model=indic_mod,tokenizer=indic_tok,text=[text],audio_code=audio_code)[0]
    else:
        transcript=speech_to_text(audio_path=web_audio_path,sarvam_api=api_key)
        translated=text_to_text(text=transcript,sarvam_api=api_key,src_lan=sarvam_lang_codes['English'],tg_lan=sarvam_lang_codes['Hindi'])
        '''use this line above only which is output from llm'''
    os.remove(web_audio_path)
    return translated

print(main())

        