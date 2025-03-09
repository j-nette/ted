from google import genai
from dotenv import load_dotenv

import time
import os
import speech_recognition as sr
from gtts import gTTS

# For Audio File
from mutagen.mp3 import MP3
import subprocess

load_dotenv()

client = genai.Client(api_key = os.getenv('KEY'))

# This is the user input we're getting from somewhere else
user_speech = "" # Change to test

# Update the contents variable into a usable string
prompt_modifier = ""


audio_file_path = "./response.mp3"

def get_length():
    audio = MP3(audio_file_path)
    length = audio.info.length + 1 # extra second as a buffer (waiting for file to load)
    return length


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
    
def text_to_speech(text: str):
    print("Ted: ", text)
    speaker = gTTS(text = text, lang = "en", slow = False, tld = 'ca')

    # Store, open, and cleanup temporary audio file
    speaker.save(audio_file_path) 
    audio_process = subprocess.Popen(["start", audio_file_path], shell=True)
    time.sleep(get_length()) # delay to avoid cleaning the file up before it is done playing
    if audio_process.poll() is None:
        audio_process.terminate()
        audio_process.wait()

    os.remove(audio_file_path)

#response = client.models.generate_content(
    #model="gemini-2.0-flash", contents=prompt_modifier+user_speech)



listen = speech_to_text()
if listen is not False:
    text_to_speech(listen)

