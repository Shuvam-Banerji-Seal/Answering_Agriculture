import os
# Disable Torch compile & inductor globally (must be set before importing torch)
os.environ["TORCH_COMPILE_DISABLE"] = "1"      # disable torch.compile
os.environ["TORCHINDUCTOR_DISABLE"] = "1"

import streamlit as st
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *
from utilis import speech_to_text ,inference,speech_to_text_bharat, translate_indic
import os
from model import llm_model,model_tokenizer,login_in,ai_bharat ,load_indic_trans

float_init()


def initial_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello there !! how  may can I help you today",
            }
        ]


initial_session_state()
st.title(" Agricultural bot 🤖 ")

#---------------------------------mere models ------------------------------
# @st.cache_resource
# def load_model():
#     login_in()
#     llm,device=llm_model(quantization=False)
#     tokenizer=model_tokenizer()
#     return llm, device, tokenizer
# llm, device, tokenizer = load_model()

@st.cache_resource
def ai_bharat_load():
    ai_b=ai_bharat()
    return ai_b
ai_bha=ai_bharat_load()

@st.cache_resource
def indic_load():
    sl,tl=load_indic_trans()
    return sl,tl
indic_mod,indic_tok=indic_load()

    
footer_container=st.container()
with footer_container:
    audio_record=audio_recorder()

footer_container.float('bottom:0rem;')
for messages in st.session_state.messages:
    with st.chat_message(name=messages['role']):
        st.write(messages['content'])


if audio_record:
    st.audio(audio_record, format="audio/wav")
    with st.spinner('Transcribing.....'):
        web_audio_path='temp_audio.wav'
        with open(web_audio_path,'wb') as f:
            f.write(audio_record)
        
        # transcript=speech_to_text(audio_path=web_audio_path)
        text=speech_to_text_bharat(model=ai_bha,audio_path=web_audio_path)
        print('ye jaa raha transcript ke liye' )
        print([text])
        transcript=translate_indic(model=indic_mod,tokenizer=indic_tok,text=[text])[0]

        if transcript:
            st.session_state.messages.append({
                'role':'user',
                'content': transcript
            })

            with st.chat_message(name='user'):
                st.write(transcript)
            os.remove(web_audio_path)

# if st.session_state.messages[-1]['role'] != "assistant":
#     with st.chat_message('assistant'):
#         with st.spinner('Thinking 🤔.....'):
#             # final_response=generate(st.session_state.messages)
#             final_response=inference(model=llm,query=transcript,device=device,tokenizer=tokenizer)
#             print(f'final response me ye mila hai ----------------------->{final_response}')
#         st.write(final_response)
#         st.session_state.messages.append({
#             'role':'assistant',
#             'content':final_response
#         })
#         print('final response likh diya hai ')