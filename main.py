from google import genai
from dotenv import load_dotenv

import time
import os
import speech_recognition as sr
from gtts import gTTS

load_dotenv()

client = genai.Client(api_key = os.getenv('KEY'))

# This is the user input we're getting from somewhere else
user_speech = "" # Change to test

# Update the contents variable into a usable string
prompt_modifier = ""

def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as mic:
        print("listening...")
        audio = recognizer.listen(mic)
    try:
        text = recognizer.recognize_google(audio)
        print("Me :", text)
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio.")
        return False
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition; {0}".format(e)) 
        return False

#response = client.models.generate_content(
    #model="gemini-2.0-flash", contents=prompt_modifier+user_speech)



response = speech_to_text()
print(response)
