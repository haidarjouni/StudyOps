from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Thread

User = get_user_model()


class ThreadListCreateTest(APITestCase):
    def setUp(self):
        self.url = reverse("thread-list")
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


class ThreadDetailTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="thread_owner",
            password="test-password",
        )
        self.other_user = User.objects.create_user(
            username="other_user",
            password="test-password",
        )
        self.thread = Thread.objects.create(user=self.user, title="My study plan")
        self.other_thread = Thread.objects.create(
            user=self.other_user, title="Someone else's plan"
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_own_thread(self):
        response = self.client.get(reverse("thread-detail", args=[self.thread.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.thread.id))
        self.assertEqual(response.data["title"], "My study plan")

    def test_cannot_retrieve_another_users_thread(self):
        response = self.client.get(reverse("thread-detail", args=[self.other_thread.id]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_own_thread(self):
        response = self.client.delete(reverse("thread-detail", args=[self.thread.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Thread.objects.filter(id=self.thread.id).exists())
        self.assertTrue(Thread.objects.filter(id=self.other_thread.id).exists())

    def test_cannot_delete_another_users_thread(self):
        response = self.client.delete(reverse("thread-detail", args=[self.other_thread.id]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Thread.objects.filter(id=self.other_thread.id).exists())

    def test_anonymous_user_cannot_retrieve_or_delete_thread(self):
        self.client.force_authenticate(user=None)
        url = reverse("thread-detail", args=[self.thread.id])

        self.assertEqual(self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Thread.objects.filter(id=self.thread.id).exists())
