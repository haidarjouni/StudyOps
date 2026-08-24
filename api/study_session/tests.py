from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.test import APITestCase
from study_task.models import StudyTask
from subject.models import Subject

from .models import StudySession

User = get_user_model()


class StudySessionViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="student",
            password="testpassword",
        )
        self.subject = Subject.objects.create(
            user=self.user,
            name="Computer Science",
            code="CS101",
            semester=1,
        )
        self.task = StudyTask.objects.create(
            user=self.user,
            subject=self.subject,
            title="Study algorithms",
            description="Review the sorting chapter.",
            task_type=StudyTask.TaskType.STUDY,
            task_status=StudyTask.TaskStatus.TODO,
            task_priority=StudyTask.TaskPriority.HIGH,
            estimated_minutes=120,
            due_date="2026-09-15T18:00:00Z",
        )
        self.session = StudySession.objects.create(
            user=self.user,
            subject=self.subject,
            start_at="2026-09-10T18:00:00Z",
            end_at="2026-09-10T19:00:00Z",
            status=StudySession.SessionStatus.SCHEDULED,
        )

        self.other_user = User.objects.create_user(
            username="otherstudent",
            password="testpassword",
        )
        self.other_subject = Subject.objects.create(
            user=self.other_user,
            name="Physics",
            code="PH101",
            semester=1,
        )
        self.other_task = StudyTask.objects.create(
            user=self.other_user,
            subject=self.other_subject,
            title="Study mechanics",
            description="Review Newton's laws.",
            task_type=StudyTask.TaskType.EXAM,
            task_status=StudyTask.TaskStatus.TODO,
            task_priority=StudyTask.TaskPriority.MEDIUM,
            estimated_minutes=90,
            due_date="2026-09-16T18:00:00Z",
        )
        self.other_session = StudySession.objects.create(
            user=self.other_user,
            subject=self.other_subject,
            start_at="2026-09-11T18:00:00Z",
            end_at="2026-09-11T19:00:00Z",
            status=StudySession.SessionStatus.SCHEDULED,
        )

        self.create_data = {
            "subject_id": self.subject.pk,
            "task_id": self.task.pk,
            "start_at": "2026-09-12T18:00:00Z",
            "end_at": "2026-09-12T19:00:00Z",
            "status": "scheduled",
        }

        self.client.force_authenticate(user=self.user)

    def test_create_study_session(self):
        response = self.client.post(
            reverse("study_session-list"),
            self.create_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_session = StudySession.objects.get(pk=response.data["id"])
        self.assertEqual(created_session.user, self.user)
        self.assertEqual(created_session.subject, self.subject)
        self.assertEqual(created_session.task, self.task)
        self.assertEqual(response.data["subject"]["id"], self.subject.pk)
        self.assertEqual(response.data["task"]["id"], self.task.pk)

    def test_user_can_only_access_own_sessions(self):
        list_response = self.client.get(reverse("study_session-list"))
        other_detail_response = self.client.get(
            reverse("study_session-detail", args=[self.other_session.pk])
        )

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)
        self.assertEqual(list_response.data[0]["id"], self.session.pk)
        self.assertEqual(
            other_detail_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_retrieve_study_session(self):
        response = self.client.get(
            reverse("study_session-detail", args=[self.session.pk])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.session.pk)
        self.assertEqual(response.data["subject"]["id"], self.subject.pk)

    def test_update_study_session(self):
        update_data = {
            "subject_id": self.subject.pk,
            "start_at": "2026-09-10T20:00:00Z",
            "end_at": "2026-09-10T21:30:00Z",
            "status": "completed",
        }

        response = self.client.put(
            reverse("study_session-detail", args=[self.session.pk]),
            update_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.session.refresh_from_db()
        self.assertEqual(self.session.status, update_data["status"])
        self.assertEqual(
            self.session.start_at,
            parse_datetime(update_data["start_at"]),
        )
        self.assertEqual(
            self.session.end_at,
            parse_datetime(update_data["end_at"]),
        )

    def test_delete_study_session(self):
        response = self.client.delete(
            reverse("study_session-detail", args=[self.session.pk])
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(StudySession.objects.filter(pk=self.session.pk).exists())
        self.assertTrue(StudySession.objects.filter(pk=self.other_session.pk).exists())

    def test_rejects_invalid_subject_and_time_range(self):
        invalid_subject_data = {
            **self.create_data,
            "subject_id": self.other_subject.pk,
        }
        invalid_time_data = {
            **self.create_data,
            "start_at": "2026-09-12T20:00:00Z",
            "end_at": "2026-09-12T19:00:00Z",
        }

        invalid_subject_response = self.client.post(
            reverse("study_session-list"),
            invalid_subject_data,
            format="json",
        )
        invalid_time_response = self.client.post(
            reverse("study_session-list"),
            invalid_time_data,
            format="json",
        )

        self.assertEqual(
            invalid_subject_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("subject_id", invalid_subject_response.data)
        self.assertEqual(
            invalid_time_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("end_at", invalid_time_response.data)

    def test_rejects_another_users_task(self):
        response = self.client.post(
            reverse("study_session-list"),
            {**self.create_data, "task_id": self.other_task.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("task_id", response.data)

    def test_rejects_task_from_a_different_subject(self):
        another_subject = Subject.objects.create(
            user=self.user,
            name="Mathematics",
            code="MATH101",
            semester=1,
        )

        response = self.client.post(
            reverse("study_session-list"),
            {**self.create_data, "subject_id": another_subject.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("task_id", response.data)

    def test_rejects_completed_or_cancelled_tasks(self):
        for task_status in (
            StudyTask.TaskStatus.DONE,
            StudyTask.TaskStatus.CANCELLED,
        ):
            self.task.task_status = task_status
            self.task.save(update_fields=["task_status"])

            response = self.client.post(
                reverse("study_session-list"),
                self.create_data,
                format="json",
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("task_id", response.data)

    def test_rejects_overlapping_sessions(self):
        response = self.client.post(
            reverse("study_session-list"),
            {
                **self.create_data,
                "start_at": "2026-09-10T18:30:00Z",
                "end_at": "2026-09-10T19:30:00Z",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("start_at", response.data)

    def test_allows_adjacent_sessions_and_ignores_cancelled_sessions(self):
        adjacent_response = self.client.post(
            reverse("study_session-list"),
            {
                **self.create_data,
                "start_at": "2026-09-10T19:00:00Z",
                "end_at": "2026-09-10T20:00:00Z",
            },
            format="json",
        )
        self.session.status = StudySession.SessionStatus.CANCELLED
        self.session.save(update_fields=["status"])
        replacement_response = self.client.post(
            reverse("study_session-list"),
            {
                **self.create_data,
                "start_at": "2026-09-10T18:00:00Z",
                "end_at": "2026-09-10T19:00:00Z",
            },
            format="json",
        )

        self.assertEqual(adjacent_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(replacement_response.status_code, status.HTTP_201_CREATED)

    def test_authentication_is_required(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(reverse("study_session-list"))

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
