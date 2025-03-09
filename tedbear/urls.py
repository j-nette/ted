# tedbear/urls.py
from django.urls import path
from .views import home_view, chat_view, summarize_view  # Import summarize_view

urlpatterns = [
    path('', home_view, name='home'),
    path('chat/', chat_view, name='chat_view'),  # changed to match the template
    path('summary/', summarize_view, name='summarize_view'),
]
