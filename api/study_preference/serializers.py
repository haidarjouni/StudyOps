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
        earliest = data.get(
            "earliest_study_time",
            getattr(self.instance, "earliest_study_time", None),
        )

        latest = data.get(
            "latest_study_time",
            getattr(self.instance, "latest_study_time", None),
        )
        if earliest is not None and latest is not None:
            if earliest >= latest:
                raise serializers.ValidationError(
                    {
                        "latest_study_time": (
                            "Latest study time must be after earliest study time."
                        )
                    }
                )
        return data
