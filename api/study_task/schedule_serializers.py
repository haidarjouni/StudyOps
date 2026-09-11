from rest_framework import serializers
from study_session.serializers import StudySessionSerializer

from .serializers import StudyTaskSerializer


class ScheduleItemCreateSerializer(serializers.Serializer):
    task = StudyTaskSerializer()
    sessions = StudySessionSerializer(many=True, allow_empty=False)

    def validate(self, attrs):
        task = attrs["task"]
        # check if task status is todo
        if task.get("task_status", "todo") != "todo":
            raise serializers.ValidationError(
                {"task": {"task_status": "A scheduled task must start as todo."}}
            )

        session_errors = {}
        for index, session in enumerate(attrs["sessions"]):
            errors = {}
            # check if session subject matches task subject
            if session["subject"] != task["subject"]:
                errors["subject_id"] = "The task and session subjects must match."
            # check if session has a task id, it should not have one since the endpoint creates and links it
            if session.get("task") is not None:
                errors["task_id"] = (
                    "Do not provide a task ID; this endpoint creates and links it."
                )
            # check if session status is scheduled
            if session.get("status", "scheduled") != "scheduled":
                errors["status"] = "A new study session must start as scheduled."
            # append the index of the session and the errors to the session_errors dictionary if there are any errors
            if errors:
                session_errors[index] = errors
        # if there are any session errors, raise a validation error with the session_errors dictionary
        if session_errors:
            raise serializers.ValidationError({"sessions": session_errors})

        return attrs


class ScheduleCreateSerializer(serializers.Serializer):
    # accepts many drafts, each draft is a dictionary with a task and a list of sessions
    drafts = ScheduleItemCreateSerializer(many=True, allow_empty=False)
