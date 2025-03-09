from django.shortcuts import render
from django.http import HttpResponse
from google import genai
import os
import datetime

INACTIVITY_THRESHOLD = datetime.timedelta(seconds=10)

def chat_view(request):
    # Retrieve conversation data and conversation flag from session.
    conversation = request.session.get("conversation", [])
    conversation_started = request.session.get("conversation_started", False)
    last_activity_iso = request.session.get("last_activity")
    # now = datetime.datetime.now()

    # Check for inactivity and generate summary if needed.
    # if last_activity_iso:
    #     last_activity = datetime.datetime.fromisoformat(last_activity_iso)
    #     if now - last_activity > INACTIVITY_THRESHOLD and conversation:
    #         summary_prompt = (
    #             "The conversation has ended due to inactivity. Based on the following transcript, provide a summary that includes:\n"
    #             "- Mood of the day\n"
    #             "- General trend of mood throughout the week\n"
    #             "- A summary of the conversation\n\n"
    #             "Transcript:\n" + "\n".join([msg["text"] for msg in conversation])
    #         )
    #         api_key = os.environ.get("GENAI_API_KEY")
    #         if api_key:
    #             try:
    #                 client = genai.Client(api_key=api_key)
    #                 response = client.models.generate_content(
    #                     model="gemini-2.0-flash",
    #                     contents=summary_prompt
    #                 )
    #                 summary_text = response.text
    #                 conversation.append({'sender': 'bear', 'text': "Summary:\n" + summary_text})
    #             except Exception as e:
    #                 conversation.append({
    #                     'sender': 'bear',
    #                     'text': f"An error occurred while generating the summary: {e}"
    #                 })
    #         else:
    #             conversation.append({
    #                 'sender': 'bear',
    #                 'text': "Error: No GENAI_API_KEY found. Please configure your environment."
    #             })
    #         # Clear conversation and reset conversation flag.
    #         conversation = []
    #         conversation_started = False
    #         request.session["conversation"] = conversation
    #         request.session["conversation_started"] = conversation_started
    #         request.session["last_activity"] = now.isoformat()
    #         return render(request, 'chat.html', {'messages': conversation})

    if request.method == 'POST':
        user_message = request.POST.get('user_message', 'Give me food')

        # If conversation hasn't started, enforce the trigger phrase.
        if not conversation_started:
            if "hey ted" not in user_message.lower():
                conversation.append({
                    'sender': 'bear',
                    'text': "Please start your conversation with 'hey ted' to get a response."
                })
                request.session["conversation"] = conversation
                return render(request, 'chat.html', {'messages': conversation})
            else:
                # Conversation is now started. Optionally, you could remove the trigger phrase from the message.
                conversation_started = True
                request.session["conversation_started"] = conversation_started

        # Append the user's message.
        conversation.append({'sender': 'user', 'text': user_message})
        # Update last activity timestamp.
        # request.session["last_activity"] = now.isoformat()

        # Create an engineered prompt for Gemini.
        engineered_prompt = (
            """You are Ted, a friendly, empathetic therapy teddy bear. 
            You help the user organize their thoughts and track their emotional trends. 
            You converse naturally, asking clarifying questions if needed, and providing empathetic responses.
            At the end of the conversation, summarize the user based on what they said by: 
            - mood of the day
            - general trend of mood throughout the week
            - the conversation
            """
        )
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

        # Save the updated conversation and conversation state.
        request.session["conversation"] = conversation

    return render(request, 'chat.html', {'messages': conversation})


def home_view(request):
    return render(request, 'home.html')
