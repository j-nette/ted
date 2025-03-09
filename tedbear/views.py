from django.shortcuts import render
from django.http import HttpResponse
from google import genai
import os

def chat_view(request):
    # Retrieve the conversation from the session, or initialize it if not present.
    conversation = request.session.get("conversation", [
        {'sender': 'bear', 'text': 'Hello! I am Ted. Ask me anything!'},
        {'sender': 'user', 'text': 'Hey Ted, how are you doing today?'},
        {'sender': 'bear', 'text': 'I am doing great, thanks for asking!'},
    ])

    if request.method == 'POST':
        user_message = request.POST.get('user_message', '')
        # Append the user's new message to the conversation.
        conversation.append({'sender': 'user', 'text': user_message})

        # Create an engineered prompt that includes context and instructions.
        engineered_prompt = (
            """ You are Ted, a friendly, empathetic therapy teddy bear. 
        You help the user organize their thoughts and track their emotional trends. 
        You converse naturally, asking clarifying questions if needed, 
        and providing empathetic responses.
        """
        )

        # Combine the engineered prompt with the user's latest message.
        full_prompt = engineered_prompt + "\nUser: " + user_message + "\nTed:"

        # --- GEMINI INTEGRATION ---
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

        # Save the updated conversation back into the session.
        request.session["conversation"] = conversation

    return render(request, 'chat.html', {'messages': conversation})


def home_view(request):
    return render(request, 'home.html')
