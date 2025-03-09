# tedbear/views.py

from django.shortcuts import render
from django.http import HttpResponse
from google import genai
import os

def chat_view(request):
    # Dummy chat messages to display on page load
    messages = [
        {'sender': 'bear', 'text': 'Hello! I am Ted. Ask me anything!'},
        {'sender': 'user', 'text': 'Hey Ted, how are you doing today?'},
        {'sender': 'bear', 'text': 'I am doing great, thanks for asking!'},
    ]

    if request.method == 'POST':
        user_message = request.POST.get('user_message', '')

        # Add the user's message to the chat
        messages.append({'sender': 'user', 'text': user_message})

        # --- GEMINI INTEGRATION ---
        # 1. Retrieve the API key from environment (settings or .env)
        api_key = os.environ.get("GENAI_API_KEY")  # or from your settings.py
        if not api_key:
            messages.append({
                'sender': 'bear',
                'text': "Error: No GENAI_API_KEY found. Please configure your environment."
            })
        else:
            try:
                # 2. Initialize the Gemini client
                client = genai.Client(api_key=api_key)

                # 3. Send the user’s message to the Gemini model
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=user_message
                )

                # 4. Get the AI's response text
                ai_response = response.text

                # 5. Add the AI's response to the chat
                messages.append({'sender': 'bear', 'text': ai_response})

            except Exception as e:
                # Handle any errors from the API call
                messages.append({
                    'sender': 'bear',
                    'text': f"An error occurred while communicating with Gemini: {e}"
                })

    return render(request, 'chat.html', {'messages': messages})

def home_view(request):
    return render(request, 'home.html')
