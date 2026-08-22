from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import SignUpSerializer
from .utils import set_jwt_cookies


# Create your views here.
class SignUpView(generics.CreateAPIView):  # view to handle the signup process
    serializer_class = SignUpSerializer
    permission_classs = [AllowAny]  # allow any user to access this view


class TokenObtainPairView(
    TokenObtainPairView
):  # view to handle the token obtain process
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        access_token = response.data["access"]
        refresh_token = response.data["refresh"]

        response.data.pop("access")
        response.data.pop("refresh")

        response = set_jwt_cookies(
            response=response, access=access_token, refresh=refresh_token
        )

        response.data = {
            "message": "Login successful.",
        }
        return response
