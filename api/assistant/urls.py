from django.urls import path

from .views import AssistantView

urlpatterns =[
    path("chat/", AssistantView.as_view(), name="assistant-chat"),
]