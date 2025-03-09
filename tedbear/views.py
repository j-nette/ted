import json
from django.shortcuts import render
from django.http import JsonResponse
from google import genai
import tempfile
import speech_recognition as sr
import os
from pydub import AudioSegment

def home_view(request):
    return render(request, 'home.html')

def send_prompt_to_ai(prompt):
    # Build the prompt for the AI.
    engineered_prompt = (
        "You are Ted, a friendly, empathetic therapy stuffed teddy bear. Please do not provide any actions, like asterisk actions. "
        "Your role is to help users organize their thoughts, track their emotions, and provide a safe space for them to express themselves. "
        "Respond with empathy, ask clarifying questions, and avoid giving medical advice. "
        "If the user seems to be in distress, gently encourage them to seek professional help."
    )
    full_prompt = engineered_prompt + "\nUser: " + prompt + "\nTed:"

    api_key = os.environ.get("GENAI_API_KEY")

    if not api_key:
        return "Error: No GENAI_API_KEY found. Please configure your environment."
    else:
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=full_prompt
            )
            return response.text

        except Exception as e:
            return "An error occurred while communicating with Gemini."

def chat_view(request):
    # Initialize the conversation from the session if it exists, otherwise start with an empty list.
    conversation = request.session.get('conversation', [])

    # Handle AJAX POST request (from Fetch)
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Get the user message from the POST data.
        user_message = request.POST.get('user_message', '')
        conversation.append({'sender': 'user', 'text': user_message})

        resp = send_prompt_to_ai(user_message)

        conversation.append({'sender': 'bear', 'text': resp})

        # Save the updated conversation to the session.
        # request.session['conversation'] = conversation

        # Return JSON so that your JavaScript can process it.
        return JsonResponse({'messages': conversation})

    # For GET requests (or non-AJAX POST), render the chat template.
    return render(request, 'chat.html', {
        'messages': conversation,
        'conversation_history': json.dumps(conversation)
    })

def summarize_view(request):
    # Retrieve the conversation from the session.
    conversation = request.session.get('conversation', [])

    # Generate the summary prompt.
    summary_prompt = (
        "Provide a concise, bullet-point summary of the conversation for mental healthcare workers. "
        "Do not bold it."
        "Include:\n"
        "- Emotional State: User's current mood and emotional tone.\n"
        "- Key Themes: Main topics or concerns discussed.\n"
        "- Stressors: Specific stressors or triggers mentioned.\n"
        "- Coping: Coping strategies used or suggested.\n"
        "- Follow-Up: Potential areas for follow-up or intervention.\n\n"
        "Transcript:\n" + "\n".join([msg["text"] for msg in conversation])
    )

    # Generate the summary using the AI model.
    api_key = os.environ.get("GENAI_API_KEY")
    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=summary_prompt
            )
            summary_text = response.text
        except Exception as e:
            summary_text = f"An error occurred while generating the summary: {e}"
    else:
        summary_text = "Error: No GENAI_API_KEY found. Please configure your environment."

    # Clear the conversation from the session after summarization.
    request.session['conversation'] = []

    # Render the summary template.
    return render(request, 'summary.html', {
        'summary': summary_text
    })




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


    print("HELLO")

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
                if time.time() - last_speech_time > 5:
                    print("Silence detected, stopping listen...")
                    break

            except sr.WaitTimeoutError:
                # If no speech is detected during the listen timeout
                if time.time() - last_speech_time > 5:
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



import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
    
def voice_view(request):

    print("HELLO 1")

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':

        transcription = speech_to_text()
        res = send_prompt_to_ai(transcription)
        
        return JsonResponse({'response': res})
    else:
        # For GET requests, render your voice chat template.
        return render(request, 'voice.html')