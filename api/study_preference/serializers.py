
from rest_framework import serializers

from .models import StudyPreference


class StudyPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyPreference
        fields = (
            "timezone",
            "earliest_study_time",
            "latest_study_time",
            "preferred_session_minutes",
            "buffer_minutes",
        )
    def validate(self, data):
        if data["earliest_study_time"] >= data["latest_study_time"]:
            raise serializers.ValidationError(
                "Earliest study time must be before latest study time."
            )
        return data