from django.shortcuts import render
from requests import Response
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .serializers import SignUpSerializer
from .utils import set_jwt_cookies


# Create your views here.
class SignUpView(generics.CreateAPIView):  # view to handle the signup process
    serializer_class = SignUpSerializer
    permission_classses = [AllowAny]  # allow any user to access this view


class CookieTokenObtainPairView(
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


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {"error": "Refresh token not found in cookies."}, status=400
            )
        serializer = self.get_serializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = serializer.validated_data

        response = Response(
            {"message": "Token refreshed successfully."},
            status=status.HTTP_200_OK,
        )

        response = set_jwt_cookies(
            response=response, access=tokens["access"], refresh=tokens["refresh"]
        )

        response.data = {
            "message": "Token refreshed successfully.",
        }
        return response


class LogoutView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        refresh_token = RefreshToken(request.COOKIES.get("refresh_token"))

        if not refresh_token:
            return Response(
                {"error": "Refresh token not found in cookies."},
                status=400,
            )

        refresh_token.blacklist()

        response = Response(
            {"message": "Logout successful."},
            status=status.HTTP_200_OK,
        )

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response
