import json
from django.shortcuts import render
from google import genai
import os

def summarize_view(request):
    # Retrieve the conversation from the session
    conversation = request.session.get('conversation', [])

    # Generate the summary prompt
    summary_prompt = (
        "Provide a concise, bullet-point summary of the conversation for mental healthcare workers. Include:\n"
        "- Emotional State: User's current mood and emotional tone.\n"
        "- Key Themes: Main topics or concerns discussed.\n"
        "- Stressors: Specific stressors or triggers mentioned.\n"
        "- Coping: Coping strategies used or suggested.\n"
        "- Follow-Up: Potential areas for follow-up or intervention.\n\n"
        "Transcript:\n" + "\n".join([msg["text"] for msg in conversation])
    )

    # Generate the summary using the AI model
    api_key = os.environ.get("GENAI_API_KEY")
    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.0-flash",  # Fix the typo here
                contents=summary_prompt
            )
            summary_text = response.text
        except Exception as e:
            summary_text = f"An error occurred while generating the summary: {e}"
    else:
        summary_text = "Error: No GENAI_API_KEY found. Please configure your environment."

    # Clear the conversation from the session after summarization
    request.session['conversation'] = []

    # Render the summary template
    return render(request, 'summary.html', {
        'summary': summary_text
    })

def chat_view(request):
    # Initialize the conversation from the session if it exists, otherwise start with an empty list.
    conversation = request.session.get('conversation', [])

    if request.method == 'POST':
        # Check if the summarize button was clicked.
        if 'summarize' in request.POST:
            summary_prompt = (
                "Provide a concise, bullet-point summary of the conversation for mental healthcare workers. Do not include ** for it. Include:\n"
                "- Emotional State: User's current mood and emotional tone.\n"
                "- Key Themes: Main topics or concerns discussed.\n"
                "- Stressors: Specific stressors or triggers mentioned.\n"
                "- Coping: Coping strategies used or suggested.\n"
                "- Follow-Up: Potential areas for follow-up or intervention.\n\n"
                "Transcript:\n" + "\n".join([msg["text"] for msg in conversation])
            )
            api_key = os.environ.get("GENAI_API_KEY")
            if api_key:
                try:
                    client = genai.Client(api_key=api_key)
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=summary_prompt
                    )
                    summary_text = response.text
                    conversation.append({'sender': 'bear', 'text': "Summary:\n" + summary_text})
                except Exception as e:
                    conversation.append({
                        'sender': 'bear',
                        'text': f"An error occurred while generating the summary: {e}"
                    })
            else:
                conversation.append({
                    'sender': 'bear',
                    'text': "Error: No GENAI_API_KEY found. Please configure your environment."
                })
            # After summarization, clear the conversation so it does not persist.
            rendered_conversation = conversation.copy()
            conversation = []
            # Save the updated conversation to the session.
            request.session['conversation'] = conversation
            return render(request, 'chat.html', {
                'messages': rendered_conversation,
                'conversation_history': json.dumps(conversation)
            })

        # Handle a new chat message.
        user_message = request.POST.get('user_message', '')
        conversation.append({'sender': 'user', 'text': user_message})

        # Build the prompt for the AI.
        engineered_prompt = (
            """You are Ted, a friendly, empathetic therapy stuffed teddy bear. Please do not provide any actions, like asterick actions.
        Your role is to help users organize their thoughts, track their emotions, and provide a safe space for them to express themselves. 
        Respond with empathy, ask clarifying questions, and avoid giving medical advice. 
        If the user seems to be in distress, gently encourage them to seek professional help.
        """
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

    # Render the conversation; conversation_history is carried as a JSON string.
    return render(request, 'chat.html', {
        'messages': conversation,
        'conversation_history': json.dumps(conversation)
    })

def home_view(request):
    return render(request, 'home.html')
