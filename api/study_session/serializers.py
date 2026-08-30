from rest_framework import serializers
from study_task.models import StudyTask
from study_task.serializers import StudyTaskSerializer
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
            "task_id",
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

        if task is not None and task.task_status in {
            StudyTask.TaskStatus.DONE,
            StudyTask.TaskStatus.CANCELLED,
        }:
            raise serializers.ValidationError(
                "You cannot schedule a completed or cancelled task."
            )

        return task

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
        status = attrs.get(
            "status",
            getattr(
                self.instance,
                "status",
                StudySession.SessionStatus.SCHEDULED,
            ),
        )

        errors = {}

        if start_at and end_at and start_at >= end_at:
            errors["end_at"] = "End time must be later than start time."

        if task is not None and subject is not None:
            if task.subject_id != subject.id:
                errors["task_id"] = (
                    "The task and study session must belong to the same subject."
                )

        if (
            start_at
            and end_at
            and start_at < end_at
            and status != StudySession.SessionStatus.CANCELLED
        ):
            request = self.context["request"]
            overlapping_sessions = StudySession.objects.filter(
                user=request.user,
                start_at__lt=end_at,
                end_at__gt=start_at,
            ).exclude(status=StudySession.SessionStatus.CANCELLED)

            if self.instance is not None:
                overlapping_sessions = overlapping_sessions.exclude(pk=self.instance.pk)

            if overlapping_sessions.exists():
                errors["start_at"] = "This session overlaps an existing session."

        if errors:
            raise serializers.ValidationError(errors)

        return attrs
