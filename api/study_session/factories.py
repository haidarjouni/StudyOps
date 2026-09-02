from datetime import timedelta

import factory
from django.utils import timezone

from study_session.models import StudySession
from study_task.factories import StudyTaskFactory
from accounts.factories import UserFactory
from subject.factories import SubjectFactory

def tomorrow_at_18():
    return (
        timezone.localtime()
        .replace(hour=18, minute=0, second=0, microsecond=0)
        + timedelta(days=1)
    )


class StudySessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StudySession
        django_get_or_create = ("user", "task", "start_at")

    user = factory.SubFactory(UserFactory)

    subject = factory.SubFactory(
        SubjectFactory,
        user=factory.SelfAttribute("..user"),
    )

    task = factory.SubFactory(
        StudyTaskFactory,
        user=factory.SelfAttribute("..user"),
        subject=factory.SelfAttribute("..subject"),
    )

    start_at = factory.LazyFunction(tomorrow_at_18)

    end_at = factory.LazyAttribute(
        lambda session: session.start_at + timedelta(minutes=45)
    )

    status = StudySession.SessionStatus.SCHEDULED