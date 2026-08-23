from rest_framework import serializers

from .models import StudyTask


class StudyTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyTask
        fields = (
            "id",
            "user",
            "subject",
            "title",
            "description",
            "task_type",
            "task_status",
            "task_priority",
            "estimated_minutes",
            "due_date",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "created_at",
            "updated_at",
        )

    def validate_subject(self, subject):
        request = self.context["request"]

        if subject.user_id != request.user.id:
            raise serializers.ValidationError(
                "You cannot assign a task to another user's subject."
            )

        return subject
