from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.dateparse import parse_time
from rest_framework import status
from rest_framework.test import APITestCase
from study_preference.models import StudyPreference

User = get_user_model()


# Create your tests here.
class StudyPreferenceTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)
        self.preference_data = {
            "timezone": "Asia/Beirut",
            "earliest_study_time": "08:00:00",
            "latest_study_time": "21:30:00",
            "preferred_session_minutes": 45,
            "buffer_minutes": 10,
        }

        self.study_preference = StudyPreference.objects.create(
            user=self.user,
            **self.preference_data,
        )

    def test_get_study_preference(self):
        response = self.client.get(reverse("study-preference-me"))
        self.assertEqual(len(StudyPreference.objects.filter(user=self.user)), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["timezone"], self.preference_data["timezone"])
        self.assertEqual(
            response.data["earliest_study_time"],
            self.preference_data["earliest_study_time"],
        )
        self.assertEqual(
            response.data["latest_study_time"],
            self.preference_data["latest_study_time"],
        )
        self.assertEqual(
            response.data["preferred_session_minutes"],
            self.preference_data["preferred_session_minutes"],
        )
        self.assertEqual(
            response.data["buffer_minutes"], self.preference_data["buffer_minutes"]
        )

    def test_update_study_preference(self):
        updated_data = {
            "timezone": "America/New_York",
            "earliest_study_time": "09:00:00",
            "latest_study_time": "22:00:00",
            "preferred_session_minutes": 60,
            "buffer_minutes": 15,
        }

        response = self.client.put(
            reverse("study-preference-me"),
            updated_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.study_preference.refresh_from_db()

        self.assertEqual(
            self.study_preference.timezone,
            updated_data["timezone"],
        )
        self.assertEqual(
            self.study_preference.earliest_study_time,
            parse_time(updated_data["earliest_study_time"]),
        )
        self.assertEqual(
            self.study_preference.latest_study_time,
            parse_time(updated_data["latest_study_time"]),
        )
        self.assertEqual(
            self.study_preference.preferred_session_minutes,
            updated_data["preferred_session_minutes"],
        )
        self.assertEqual(
            self.study_preference.buffer_minutes,
            updated_data["buffer_minutes"],
        )

    def test_anonymous_user_cannot_access_study_preference(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("study-preference-me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_updates_only_their_own_study_preference(self):
        another_user = User.objects.create_user(
            username="anotheruser",
            email="another@example.com",
            password="anotherpassword",
        )
        another_preference = StudyPreference.objects.create(
            user=another_user,
            timezone="Europe/London",
            earliest_study_time="07:00:00",
            latest_study_time="20:00:00",
            preferred_session_minutes=30,
            buffer_minutes=5,
        )

        original_timezone = self.study_preference.timezone

        self.client.force_authenticate(user=another_user)

        updated_data = {
            "timezone": "America/New_York",
            "earliest_study_time": "09:00:00",
            "latest_study_time": "22:00:00",
            "preferred_session_minutes": 60,
            "buffer_minutes": 15,
        }

        response = self.client.put(
            reverse("study-preference-me"),
            updated_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        another_preference.refresh_from_db()
        self.study_preference.refresh_from_db()

        # The second user updated their own preference.
        self.assertEqual(
            another_preference.timezone,
            updated_data["timezone"],
        )

        # The first user's preference was untouched.
        self.assertEqual(
            self.study_preference.timezone,
            original_timezone,
        )
