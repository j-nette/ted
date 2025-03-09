# tedbear/views.py
from django.shortcuts import render

def home_view(request):
    """
    Renders a home screen with a 'Talk to Ted' prompt or button.
    """
    return render(request, 'home.html')


def chat_view(request):
    """
    Displays a simple chat interface where the user can send messages
    and see dummy responses from 'Ted'.
    """
    # We'll store some dummy messages in a list for demonstration.
    # In a real app, you might store chat messages in a database or session.
    messages = [
        {'sender': 'bear', 'text': 'Hello! I am Ted. Ask me anything!'},
        {'sender': 'user', 'text': 'Hey Ted, how are you doing today?'},
        {'sender': 'bear', 'text': 'I am doing great, thanks for asking!'},
    ]

    if request.method == 'POST':
        user_message = request.POST.get('user_message', '')
        # Add the user's message
        messages.append({'sender': 'user', 'text': user_message})
        # Add a dummy response from Ted
        messages.append({'sender': 'bear', 'text': 'This is a fake response from Ted!'})

    return render(request, 'chat.html', {'messages': messages})
