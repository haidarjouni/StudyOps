from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from study_preference.models import StudyPreference
User = get_user_model()
# Create your tests here.
class SignUpTest(APITestCase):
    def test_signup_success(self):
        valid_signup_data = {
            "username": "study_student_01",
            "email": "student01@example.com",
            "password": "Orbit!Cedar9274",
            "study_preferences": {
                "timezone": "Asia/Beirut",
                "earliest_study_time": "08:00:00",
                "latest_study_time": "21:30:00",
                "preferred_session_minutes": 45,
                "buffer_minutes": 10,
            },
        }
        signup_url = reverse("signup")
        response = self.client.post(signup_url, valid_signup_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(email="student01@example.com")
        preference = StudyPreference.objects.get(user=user)
        self.assertEqual(user.email, "student01@example.com")
        self.assertTrue(user.check_password("Orbit!Cedar9274"))
        self.assertEqual(StudyPreference.objects.count(), 1)
        self.assertEqual(preference.timezone, "Asia/Beirut")
        self.assertEqual(preference.preferred_session_minutes, 45)
        self.assertEqual(preference.buffer_minutes, 10)
        self.assertTrue(StudyPreference.objects.filter(user=user).exists())
        self.assertNotIn("password", response.data)  # Ensure password is not returned in the response
        
    def test_signup_failure_validating_time(self):
        invalid_study_time_data = {
            "username": "study_student_02",
            "email": "student02@example.com",
            "password": "Comet!Forest4821",
            "study_preferences": {
                "timezone": "Asia/Beirut",
                "earliest_study_time": "21:30:00",
                "latest_study_time": "08:00:00",
                "preferred_session_minutes": 45,
                "buffer_minutes": 10,
            },
        }
        signup_url = reverse("signup")
        response = self.client.post(signup_url, invalid_study_time_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(StudyPreference.objects.count(), 0)