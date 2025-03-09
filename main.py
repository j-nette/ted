from dotenv import load_dotenv
import time
import os
import speech_recognition as sr
from gtts import gTTS
from mutagen.mp3 import MP3
import subprocess

load_dotenv()

audio_file_path = "./response.mp3"

def get_length():
    audio = MP3(audio_file_path)
    length = audio.info.length + 1  # extra second as a buffer (waiting for file to load)
    return length

def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as mic:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(mic)  # Adjusts for ambient noise level
        last_speech_time = time.time()  # Track the time of the last speech input
        user_speech = ""  # Initialize user_speech as an empty string
        
        while True:
            try:
                # Listen for speech (timeout of 1 second)
                audio = recognizer.listen(mic, timeout=1)
                print("Heard something...")

                try:
                    # Attempt to recognize the speech and append it to the existing user_speech
                    recognized_text = recognizer.recognize_google(audio)
                    print("Me: ", recognized_text)
                    user_speech += " " + recognized_text  # Append recognized speech
                    last_speech_time = time.time()  # Update last speech time
                except sr.UnknownValueError:
                    pass  # Ignore unrecognized speech
                except sr.RequestError as e:
                    print(f"Error with speech recognition service: {e}")
                    break
                
                # Check if there is silence for more than 5 seconds
                if time.time() - last_speech_time > 1:
                    print("Silence detected, stopping listen...")
                    break

            except sr.WaitTimeoutError:
                # If no speech is detected during the listen timeout
                if time.time() - last_speech_time > 2:
                    print("Silence detected, stopping listen...")
                    break
                continue

        return user_speech if user_speech else None

def text_to_speech(text: str):
    print("Ted: ", text)
    speaker = gTTS(text=text, lang="en", slow=False, tld="ca")

    # Store, open, and cleanup temporary audio file
    speaker.save(audio_file_path)

    # Cross-platform solution for playing the audio file
    if os.name == 'nt':  # For Windows
        audio_process = subprocess.Popen(["start", audio_file_path], shell=True)
    elif os.name == 'posix':  # For macOS or Linux
        audio_process = subprocess.Popen(["mpg321", audio_file_path])

    # Wait for the audio to finish playing before continuing
    time.sleep(get_length())  # Adjust the sleep time based on the audio length
    if audio_process.poll() is None:
        audio_process.terminate()
        audio_process.wait()

    # Clean up the audio file after playing
    os.remove(audio_file_path)

# Main logic to listen and respond
user_speech = speech_to_text()
if user_speech:
    text_to_speech(user_speech)
