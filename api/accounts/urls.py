from django.contrib import admin
from django.urls import path

from .views import SignUpView, TokenObtainPairView

urlpatterns = [
    path(
        "signup/", SignUpView.as_view(), name="signup"
    ),  # add a URL pattern for the signup view
    path(
        "login/", TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),  # add a URL pattern for the login view
]
