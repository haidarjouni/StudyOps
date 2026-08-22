from django.contrib import admin
from django.urls import path

from .views import SignUpView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'), #add a URL pattern for the signup view
]
