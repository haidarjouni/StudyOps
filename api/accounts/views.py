from django.shortcuts import render

from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import SignUpSerializer

# Create your views here.
class SignUpView(generics.CreateAPIView): #view to handle the signup process
    serializer_class = SignUpSerializer 
    permission_classs = [AllowAny] #allow any user to access this view