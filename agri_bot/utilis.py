from prompt import prompt_gen
import torch
import os 
from dotenv import load_dotenv
from sarvamai import SarvamAI
import re


'''this speech to text was for testing model whisper '''

# def speech_to_text(audio_path,model):
#     result = model.transcribe(audio_path)
#     return result['text']

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

def inference(model,query,device,tokenizer,max_token=500):
    ''' input as text is given apply chat template ,do retrieval then generate answer using large language model and give the output '''
    model.eval()
    with torch.inference_mode():
        print('----------------------------generate ke andar------------------------')
        print(f"------------->{query}")
        prompt=prompt_gen(query=query,tokenizer=tokenizer)
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