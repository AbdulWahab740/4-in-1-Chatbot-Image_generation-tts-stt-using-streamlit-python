import streamlit as st
from streamlit_chat import message
from itertools import zip_longest
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
import io
import openai

from PIL import Image
import requests
from gtts import gTTS
import  speech_recognition as sr
openai_key = st.secrets['OPENAI_API_KEY'] 

st.set_page_config(page_title='Mera Chatbot hai')
st.title("Personal Bot")
 
if 'entered_prompt' not in st.session_state:
    st.session_state['entered_prompt'] = ""
    
if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []
    
def submit():
    st.session_state.entered_prompt  = st.session_state.prompt_input
    st.session_state.prompt_input  = ""
    
chat = ChatOpenAI(
    temperature=0.5,
    model='gpt-3.5-turbo',
    openai_api_key=openai_key,
    max_tokens=100,
)
def build_message_list():
    zipped_messages = [SystemMessage(
        # content="You are a helpful AI assistant talking with a human. If you do not know an answer, just say 'I don't know', do not make up an answer.")]
        content = """your name is AI Mentor. You are an AI Technical Expert for Artificial Intelligence, here to guide and assist students with their AI-related questions and concerns. Please provide accurate and helpful information, and always maintain a polite and professional tone.

                1. Greet the user politely ask user name and ask how you can assist them with AI-related queries.
                2. Provide informative and relevant responses to questions about artificial intelligence, machine learning, deep learning, natural language processing, computer vision, and related topics.
                3. you must Avoid discussing sensitive, offensive, or harmful content. Refrain from engaging in any form of discrimination, harassment, or inappropriate behavior.
                4. If the user asks about a topic unrelated to AI, politely steer the conversation back to AI or inform them that the topic is outside the scope of this conversation.
                5. Be patient and considerate when responding to user queries, and provide clear explanations.
                6. If the user expresses gratitude or indicates the end of the conversation, respond with a polite farewell.
                7. Do Not generate the long paragarphs in response. Maximum Words should be 100.

                Remember, your primary goal is to assist and educate students in the field of Artificial Intelligence. Always prioritize their learning experience and well-being."""
    )]

    for human_msg, ai_msg in zip_longest(st.session_state['past'],st.session_state['generated']):
        if human_msg is not None:
            zipped_messages.append(HumanMessage(content=human_msg))
        if ai_msg is not None:
            zipped_messages.append(AIMessage(content=ai_msg))
            
def generated_message():
    
    zipped_message = build_message_list()
    ai_response  = chat(zipped_message)
    response  = ai_response.content
    
    return response

def gen(text):
    response = openai.Image.create(
        prompt=text,
        n=1,
        size='512x512',
    )
    image_url = response.data[0]['url']
    im_content = requests.get(image_url).content
    image = Image.open(io.BytesIO(im_content))
    return image

def text_to_speech(text):
    gt = gTTS(text)
    gt.save('audio.mp3')
    st.audio('audio.mp3')

def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something...")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand the audio.")
        return ""
    except sr.RequestError as e:
        print(f"Sorry, there was an error with the ASR service: {e}")
        return ""
with st.sidebar:
    options = st.radio("Select the option you want to do", ['ChatBot', 'Text-to-Speech','Speech-to-text','Imgae-generator'])
if options == 'ChatBot':
    st.text_input('YOU: ',key='prompt_input',on_change=submit)
    if st.session_state.entered_prompt != "":
        user  = st.session_state.entered_prompt
        st.session_state.past.append(user)
        response = generated_message()       
        st.session_state.generated.append(response)
        
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])-1,-1,-1):
            message(st.session_state['generated'][i],key=str(i))     
            message(st.session_state['past'],is_user=True,key=str(i)+ '_user')

elif options == 'Imgae-generator':
    text_area = st.text_input("Enter the prompt here:",max_chars=150,placeholder='Enter prompt')

    if st.button("Submit"):
        if text_area is not None:
            generated_image = gen(text_area)
            st.image(generated_image,"Generated Image")
            image_byte = io.BytesIO()
            generated_image.save(image_byte,format='png')
            st.markdown("### Download Image")
            st.write("Click the button below to download the generated image.")
            st.download_button(
                label="Download Image",
                data=image_byte.getvalue(),
                key="download_image",
                file_name="image_generated.png",
                mime="image/png"
            )

elif options == 'Text-to-Speech':
    text = st.text_area("Enter the text to convert it to voice: ",max_chars=2000,placeholder="Enter the text here(2000 characters)")
    if st.button("Submit"):
        if text is not None:
            text_to_speech(text=text)

elif options == 'Speech-to-text':
    st.write("Enter the Button to speak")
    if st.button("Speak"):
        speech_to_text()
        
