from rest_framework import serializers
from subject.models import Subject
from subject.serializers import SubjectSerializer

from .models import StudySession


class StudySessionSerializer(serializers.ModelSerializer):

    subject = SubjectSerializer(read_only=True)

    subject_id = serializers.PrimaryKeyRelatedField(
        source="subject",
        queryset=Subject.objects.all(),
        write_only=True,
    )

    class Meta:
        model = StudySession
        fields = (
            "id",
            "user",
            "subject",
            "subject_id",
            "start_at",
            "end_at",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "created_at",
            "updated_at",
        )

    def validate_subject_id(self, subject):
        request = self.context["request"]

        if subject.user_id != request.user.id:
            raise serializers.ValidationError("You cannot use another user's subject.")

        return subject

    def validate(self, attrs):
        start_at = attrs.get(
            "start_at",
            getattr(self.instance, "start_at", None),
        )
        end_at = attrs.get(
            "end_at",
            getattr(self.instance, "end_at", None),
        )

        if start_at and end_at and start_at >= end_at:
            raise serializers.ValidationError(
                {"end_at": "End time must be later than start time."}
            )

        return attrs
