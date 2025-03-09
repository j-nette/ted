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

def chat_view(request):
    # Initialize the conversation from the session if it exists, otherwise start with an empty list.
    conversation = request.session.get('conversation', [])

    # Handle AJAX POST request (from Fetch)
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Get the user message from the POST data.
        user_message = request.POST.get('user_message', '')
        conversation.append({'sender': 'user', 'text': user_message})

        # Build the prompt for the AI.
        engineered_prompt = (
            "You are Ted, a friendly, empathetic therapy stuffed teddy bear. Please do not provide any actions, like asterisk actions. "
            "Your role is to help users organize their thoughts, track their emotions, and provide a safe space for them to express themselves. "
            "Respond with empathy, ask clarifying questions, and avoid giving medical advice. "
            "If the user seems to be in distress, gently encourage them to seek professional help."
        )
        full_prompt = engineered_prompt + "\nUser: " + user_message + "\nTed:"

        api_key = os.environ.get("GENAI_API_KEY")
        if not api_key:
            conversation.append({
                'sender': 'bear',
                'text': "Error: No GENAI_API_KEY found. Please configure your environment."
            })
        else:
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=full_prompt
                )
                ai_response = response.text
                conversation.append({'sender': 'bear', 'text': ai_response})
            except Exception as e:
                conversation.append({
                    'sender': 'bear',
                    'text': f"An error occurred while communicating with Gemini: {e}"
                })

        # Save the updated conversation to the session.
        request.session['conversation'] = conversation

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

def voice_view(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Retrieve the uploaded audio file from the request.
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return JsonResponse({'error': 'No audio file provided.'}, status=400)
        
        # Save the uploaded file to a temporary location.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as temp_file:
            for chunk in audio_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        # If the file is not already WAV, convert it using pydub.
        if not audio_file.name.lower().endswith('.wav'):
            try:
                audio = AudioSegment.from_file(temp_file_path)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as wav_temp:
                    audio.export(wav_temp.name, format="wav")
                    temp_audio_path = wav_temp.name
            except Exception as e:
                os.remove(temp_file_path)
                return JsonResponse({'error': f'Error converting audio: {e}'}, status=500)
            finally:
                os.remove(temp_file_path)
        else:
            temp_audio_path = temp_file_path

        recognizer = sr.Recognizer()
        try:
            # Open the temporary audio file using SpeechRecognition.
            with sr.AudioFile(temp_audio_path) as source:
                audio_data = recognizer.record(source)
            # Use Google’s free recognition API.
            transcription = recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            transcription = "Sorry, I could not understand the audio."
        except sr.RequestError as e:
            transcription = f"Could not request results from the speech recognition service; {e}"
        finally:
            # Clean up the temporary WAV file.
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
        
        return JsonResponse({'transcription': transcription})
    else:
        # For GET requests, render your voice chat template.
        return render(request, 'voice.html')
