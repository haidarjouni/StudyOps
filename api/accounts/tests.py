from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from study_preference.models import StudyPreference

User = get_user_model()


# Create your tests here.
class SignUpTest(APITestCase):
    SIGNUP_URL = reverse("signup")

    def test_signup_success(self):
        valid_signup_data = {  # arrange
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
        response = self.client.post(
            self.SIGNUP_URL, valid_signup_data, format="json"
        )  # act
        # assert
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
        self.assertNotIn(
            "password", response.data
        )  # Ensure password is not returned in the response

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
        response = self.client.post(
            self.SIGNUP_URL, invalid_study_time_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(StudyPreference.objects.count(), 0)


class CookieTokenObtainPairTest(APITestCase):
    LOGIN_URL = reverse("cookie_token_obtain_pair")

    def setUp(self):
        self.user = User.objects.create_user(
            username="study_student_03",
            email="study_student_03@example.com",
            password="study_student_03_password",
        )

    def test_login_success(self):
        login_data = {
            "username": "study_student_03",
            "password": "study_student_03_password",
        }
        response = self.client.post(self.LOGIN_URL, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)

    def test_login_failure(self):
        invalid_login_data = {
            "username": "study_student_03",
            "password": "wrong_password",
        }
        response = self.client.post(self.LOGIN_URL, invalid_login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access_token", response.cookies)
        self.assertNotIn("refresh_token", response.cookies)


class CookieTokenRefreshTest(APITestCase):
    REFRESH_URL = reverse("cookie_token_refresh")

    def setUp(self):
        self.user = User.objects.create_user(
            username="study_student_04",
            email="study_student_04@example.com",
            password="study_student_04_password",
        )

    def test_refresh_token_success(self):
        user = self.user
        refresh = RefreshToken.for_user(user)
        self.client.cookies["refresh_token"] = str(refresh)
        response = self.client.post(self.REFRESH_URL, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

    def test_refresh_token_failure(self):
        self.client.cookies["refresh_token"] = "invalid_refresh_token"
        response = self.client.post(self.REFRESH_URL, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access_token", response.cookies)
        self.assertNotIn("refresh_token", response.cookies)


class LogoutTest(APITestCase):
    LOGOUT_URL = reverse("logout")

    def setUp(self):
        self.user = User.objects.create_user(
            username="study_student_05",
            email="study_student_05@example.com",
            password="study_student_05_password",
        )

    def test_logout_success(self):
        user = self.user
        refresh = RefreshToken.for_user(user)
        self.client.cookies["refresh_token"] = str(refresh)
        response = self.client.post(self.LOGOUT_URL, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_cookie = response.cookies["access_token"]
        refresh_cookie = response.cookies["refresh_token"]

        self.assertEqual(access_cookie.value, "")
        self.assertEqual(int(access_cookie["max-age"]), 0)

        self.assertEqual(refresh_cookie.value, "")
        self.assertEqual(int(refresh_cookie["max-age"]), 0)


class DjoserTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="study_student_05",
            email="study_student_05@example.com",
            password="study_student_05_password",
        )

    def test_djoser_me_returns_authenticated_user(self):
        user = self.user
        self.client.force_authenticate(user=user)
        response = self.client.get(reverse("user-me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], user.username)
        self.assertEqual(user.pk, response.data["id"])

    def test_djoser_me_rejects_anonymous_user(self):
        response = self.client.get(reverse("user-me"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
