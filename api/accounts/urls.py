from django.contrib import admin
from django.urls import path

from .views import (CookieTokenObtainPairView, CookieTokenRefreshView,
                    LogoutView, SignUpView)

urlpatterns = [
    path(
        "signup/", SignUpView.as_view(), name="signup"
    ),  # add a URL pattern for the signup view
    path(
        "login/", CookieTokenObtainPairView.as_view(), name="cookie_token_obtain_pair"
    ),  # add a URL pattern for the login view
    path(
        "token/refresh/", CookieTokenRefreshView.as_view(), name="cookie_token_refresh"
    ),  # add a URL pattern for the token refresh view
    path(
        "logout/", LogoutView.as_view(), name="logout"
    ),  # add a URL pattern for the logout view
]
