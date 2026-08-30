from django_filters import rest_framework as filters

from .models import StudySession


class StudySessionFilter(filters.FilterSet):
    class Meta:
        model = StudySession
        fields = {
            "subject": ["exact"],
            "task": ["exact"],
            "status": ["exact"],
            "start_at": ["gt", "gte", "lt", "lte"],
            "end_at": ["gt", "gte", "lt", "lte"],
        }
