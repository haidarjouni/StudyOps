from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User= get_user_model()
# Create your tests here.
class AssistantViewTestCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
        )
    
    def test_assistant_chat_authenticated(self):
        access_token = RefreshToken.for_user(self.user).access_token
        self.client.cookies["access_token"] = str(access_token)

        response = self.client.post(reverse("assistant-chat"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"authenticated": True})
        
    def test_assistant_chat_requires_authentication(self):
        response = self.client.post(reverse("assistant-chat"))
        self.assertEqual(response.status_code, 401)  # Unauthorized