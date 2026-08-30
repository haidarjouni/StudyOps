from django_filters import rest_framework as filters

from .models import StudyTask


class StudyTaskFilter(filters.FilterSet):
    class Meta:
        model = StudyTask
        fields = {
            "subject": ["exact"],
            "task_type": ["exact"],
            "task_status": ["exact"],
            "task_priority": ["exact"],
            "estimated_minutes": ["gte", "lte"],
            "due_date": ["gte", "lte"],
        }
