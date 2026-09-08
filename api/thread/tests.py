from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Thread

User = get_user_model()


class ThreadListCreateTest(APITestCase):
    def setUp(self):
        self.url = reverse("thread-list-create")
        self.user = User.objects.create_user(
            username="thread_owner",
            password="test-password",
        )
        self.client.force_authenticate(user=self.user)

    def test_create_thread_assigns_authenticated_user(self):
        response = self.client.post(self.url, {"title": "My study plan"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        thread = Thread.objects.get(id=response.data["id"])
        self.assertEqual(thread.user, self.user)
        self.assertEqual(thread.title, "My study plan")

    def test_list_threads_only_returns_authenticated_users_threads(self):
        Thread.objects.create(user=self.user, title="Mine")
        other_user = User.objects.create_user(
            username="other_user",
            password="test-password",
        )
        Thread.objects.create(user=other_user, title="Not mine")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Mine")

    def test_anonymous_user_cannot_create_thread(self):
        self.client.force_authenticate(user=None)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Thread.objects.count(), 0)
