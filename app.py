import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
import paho.mqtt.client as paho
import json
from gtts import gTTS
from googletrans import Translator
#Audio
import numpy as np
#Analisis de sentimiento
from textblob import TextBlob
import pandas as pd
from googletrans import Translator

def on_publish(client,userdata,result):             #create function for callback
    print("el dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received=str(message.payload.decode("utf-8"))
    st.write(message_received)

broker="157.230.214.127"
port=1883
client1= paho.Client("GIT-HUB-ISA") #Cambiar cliente
client1.on_message = on_message



st.title("Espejo mágico App")
st.subheader("Controla tu espejo por voz")

image = Image.open('voice_ctrl.jpg')

st.image(image, width=200)




st.write("Toca el Botón y habla ")

stt_button = Button(label=" Inicio ", width=200)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

if result:
    if "GET_TEXT" in result:
        st.write(result.get("GET_TEXT"))
        client1.on_publish = on_publish                            
        client1.connect(broker,port)  
        message =json.dumps({"Act1":result.get("GET_TEXT").strip()})
        ret= client1.publish("voice_ctrl_Isa", message) #Cambiar tópico

    
    try:
        os.mkdir("temp")
    except:
        pass
        

#Audio

audio_file = open('Dance.mp3', 'rb')
audio_bytes = audio_file.read()

audio_file_sad = open('Nocturne.mp3', 'rb')
audio_bytes_sad = audio_file_sad.read()

audio_file_Neutral = open('Thank.mp3', 'rb')
audio_bytes_Neutral = audio_file_Neutral.read()

translator = Translator()
with st.expander('Analizar texto'):
    text = st.text_input('Escribe por favor: ')
    if text:

        translation = translator.translate(text, src="es", dest="en")
        trans_text = translation.text
        blob = TextBlob(trans_text)
        st.write('Polarity: ', round(blob.sentiment.polarity,2))
        st.write('Subjectivity: ', round(blob.sentiment.subjectivity,2))
        x=round(blob.sentiment.polarity,2)
        if x >= 0.5:
            st.write( 'Es un sentimiento Positivo, aquí tienes musica feliz 😊')
            st.audio(audio_bytes, format='audio/ogg')
        elif x <= -0.5:
            st.write( 'Es un sentimiento Negativo, Aquí tienes musica relajante 😔')
            st.audio(audio_bytes_sad, format='audio/ogg')
        else:
            st.write( 'Es un sentimiento Neutral, aquí tienes música para que te animes 😐')
            st.audio(audio_bytes_Neutral, format='audio/ogg')




