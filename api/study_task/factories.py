from datetime import timedelta

import factory
from django.utils import timezone

from accounts.factories import UserFactory
from study_task.models import StudyTask
from subject.factories import SubjectFactory


class StudyTaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StudyTask
        django_get_or_create = ("user", "title")

    user = factory.SubFactory(UserFactory)

    # Ensure the subject belongs to the same user as the task.
    subject = factory.SubFactory(
        SubjectFactory, # creates a new subject if one doesn't exist
        user=factory.SelfAttribute("..user"), # uses the task's user for the subject's user
    )

    title = factory.Sequence(
        lambda number: f"Study task {number + 1}"
    )
    description = "Complete the required study work."
    task_type = StudyTask.TaskType.STUDY
    task_status = StudyTask.TaskStatus.TODO
    task_priority = StudyTask.TaskPriority.MEDIUM
    estimated_minutes = 120
    due_date = factory.LazyFunction(
        lambda: timezone.now() + timedelta(days=7)
    )