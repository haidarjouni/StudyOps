from datetime import time

import factory

from accounts.factories import UserFactory
from study_preference.models import StudyPreference


class StudyPreferenceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StudyPreference
        django_get_or_create = ("user",)

    user = factory.SubFactory(UserFactory)
    timezone = "Asia/Beirut"
    earliest_study_time = time(8, 0)
    latest_study_time = time(22, 0)
    preferred_session_minutes = 45
    buffer_minutes = 10