from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.test import APITestCase
from study_session.models import StudySession
from subject.models import Subject

from study_task.models import StudyTask

User = get_user_model()


class StudyTaskViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
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
            title="Study chapter 3",
            description="Review algorithms.",
            task_type=StudyTask.TaskType.STUDY,
            task_status=StudyTask.TaskStatus.TODO,
            task_priority=StudyTask.TaskPriority.MEDIUM,
            estimated_minutes=60,
            due_date="2026-09-01T18:00:00Z",
        )

        self.other_user = User.objects.create_user(
            username="testuser2",
            password="testpassword2",
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
            title="Prepare for Physics Exam",
            description="Review mechanics and complete practice questions.",
            task_type=StudyTask.TaskType.EXAM,
            task_status=StudyTask.TaskStatus.IN_PROGRESS,
            task_priority=StudyTask.TaskPriority.HIGH,
            estimated_minutes=120,
            due_date="2026-09-15T16:30:00Z",
        )

        self.create_data = {
            "subject": self.subject.pk,
            "title": "Complete Programming Assignment",
            "description": "Implement the required features and write unit tests.",
            "task_type": "assignment",
            "task_status": "todo",
            "task_priority": "high",
            "estimated_minutes": 90,
            "due_date": "2026-09-10T20:00:00Z",
        }

        self.client.force_authenticate(user=self.user)

    def test_study_task_create_view(self):
        response = self.client.post(
            reverse("studytask-list"),
            self.create_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StudyTask.objects.filter(user=self.user).count(), 2)

        created_task = StudyTask.objects.get(pk=response.data["id"])
        self.assertEqual(created_task.user, self.user)
        self.assertEqual(created_task.subject, self.subject)
        self.assertEqual(created_task.title, self.create_data["title"])

    def test_create_schedule(self):
        response = self.client.post(
            reverse("studytask-create-schedule"),
            {
                "drafts": [
                    {
                        "task": self.create_data,
                        "sessions": [
                            {
                                "subject_id": self.subject.pk,
                                "start_at": "2026-09-09T17:00:00Z",
                                "end_at": "2026-09-09T18:00:00Z",
                                "status": "scheduled",
                            },
                            {
                                "subject_id": self.subject.pk,
                                "start_at": "2026-09-10T17:00:00Z",
                                "end_at": "2026-09-10T17:30:00Z",
                                "status": "scheduled",
                            },
                        ],
                    }
                ]
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["drafts"]), 1)

        created = response.data["drafts"][0]
        task = StudyTask.objects.get(pk=created["task"]["id"])
        sessions = StudySession.objects.filter(task=task)

        self.assertEqual(task.user, self.user)
        self.assertEqual(sessions.count(), 2)
        self.assertEqual(len(created["sessions"]), 2)

    def test_create_schedule_rejects_an_empty_sessions_list(self):
        response = self.client.post(
            reverse("studytask-create-schedule"),
            {
                "drafts": [
                    {
                        "task": self.create_data,
                        "sessions": [],
                    }
                ]
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(StudyTask.objects.filter(user=self.user).count(), 1)
        self.assertEqual(StudySession.objects.filter(user=self.user).count(), 0)

    def test_study_task_list_view(self):
        response = self.client.get(reverse("studytask-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.task.pk)

    def test_delete_study_task(self):
        response = self.client.delete(reverse("studytask-detail", args=[self.task.pk]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(StudyTask.objects.filter(pk=self.task.pk).exists())
        self.assertTrue(StudyTask.objects.filter(pk=self.other_task.pk).exists())

    def test_update_study_task(self):
        update_data = {
            "subject": self.subject.pk,
            "title": "Updated Programming Assignment",
            "description": "Complete the implementation, documentation, and unit tests.",
            "task_type": "assignment",
            "task_status": "in_progress",
            "task_priority": "medium",
            "estimated_minutes": 120,
            "due_date": "2026-09-12T21:00:00Z",
        }

        response = self.client.put(
            reverse("studytask-detail", args=[self.task.pk]),
            update_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_task = StudyTask.objects.get(pk=self.task.pk)

        self.assertEqual(updated_task.subject, self.subject)
        self.assertEqual(updated_task.title, update_data["title"])
        self.assertEqual(updated_task.description, update_data["description"])
        self.assertEqual(updated_task.task_type, update_data["task_type"])
        self.assertEqual(updated_task.task_status, update_data["task_status"])
        self.assertEqual(updated_task.task_priority, update_data["task_priority"])
        self.assertEqual(
            updated_task.estimated_minutes,
            update_data["estimated_minutes"],
        )
        self.assertEqual(
            updated_task.due_date,
            parse_datetime(update_data["due_date"]),
        )

    def test_unauthorized_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("studytask-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_other_users_task(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(reverse("studytask-detail", args=[self.task.pk]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_task_with_other_users_subject(self):
        create_data = {
            "subject": self.other_subject.pk,
            "title": "Unauthorized Task",
            "description": "This task should not be created.",
            "task_type": "study",
            "task_status": "todo",
            "task_priority": "low",
            "estimated_minutes": 30,
            "due_date": "2026-09-20T18:00:00Z",
        }
        response = self.client.post(
            reverse("studytask-list"),
            create_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("subject", response.data)

    def test_filtering_by_due_date(self):
        response = self.client.get(
            reverse("studytask-list"),
            {
                "due_date__gte": "2026-09-01T00:00:00Z",
                "due_date__lte": "2026-09-30T23:59:59Z",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.task.pk)

    def test_filtering_by_task_status(self):
        response = self.client.get(
            reverse("studytask-list"),
            {"task_status": "todo"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.task.pk)
