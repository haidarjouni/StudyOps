from django.db import models


# Create your models here.
class StudySession(models.Model):
    class SessionStatus(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        "auth.user",
        on_delete=models.CASCADE,
        related_name="study_sessions",
    )
    subject = models.ForeignKey(
        "subject.Subject",
        on_delete=models.CASCADE,
        related_name="study_sessions",
    )
    task = models.ForeignKey(
        "study_task.StudyTask",
        on_delete=models.SET_NULL,
        related_name="study_sessions",
        null=True,
        blank=True,
    )
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=SessionStatus.choices,
        default=SessionStatus.SCHEDULED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
