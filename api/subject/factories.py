import factory

from accounts.factories import UserFactory
from subject.models import Subject


class SubjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Subject
        django_get_or_create = ("user", "code")

    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda number: f"Subject {number + 1}")
    code = factory.Sequence(lambda number: f"SUB{number + 1:03d}")
    semester = 1