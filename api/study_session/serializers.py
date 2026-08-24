from rest_framework import serializers
from api.study_task.models import StudyTask
from api.study_task.serializers import StudyTaskSerializer
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

    task = StudyTaskSerializer(read_only=True)
    task_id = serializers.PrimaryKeyRelatedField(
        source="task",
        queryset=StudyTask.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = StudySession
        fields = (
            "id",
            "user",
            "subject",
            "subject_id",
            "task",
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

    def validate_task_id(self, task):
        request = self.context["request"]

        if task is not None and task.user_id != request.user.id:
            raise serializers.ValidationError("You cannot use another user's task.")

        return task

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
        subject = attrs.get(
            "subject",
            getattr(self.instance, "subject", None),
        )
        task = attrs.get(
            "task",
            getattr(self.instance, "task", None),
        )

        errors = {}

        if start_at and end_at and start_at >= end_at:
            errors["end_at"] = "End time must be later than start time."

        if task is not None and subject is not None:
            if task.subject_id != subject.id:
                errors["task_id"] = (
                    "The task and study session must belong to the same subject."
                )

        if errors:
            raise serializers.ValidationError(errors)

        return attrs
