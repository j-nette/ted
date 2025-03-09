import json
from django.shortcuts import render
from django.http import JsonResponse
from google import genai
import os

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
            """You are Ted, a friendly, empathetic therapy stuffed teddy bear. Please do not provide any actions, like asterisk actions.
            Your role is to help users organize their thoughts, track their emotions, and provide a safe space for them to express themselves. 
            Respond with empathy, ask clarifying questions, and avoid giving medical advice. 
            If the user seems to be in distress, gently encourage them to seek professional help."""
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
