from django.db import models


# Create your models here.
class StudyTask(models.Model):
    class TaskType(models.TextChoices):
        ASSIGNMENT = "assignment", "Assignment"
        EXAM = "exam", "Exam"
        STUDY = "study", "General study"
        OTHER = "other", "Other"

    class TaskStatus(models.TextChoices):
        TODO = "todo", "To do"
        IN_PROGRESS = "in_progress", "In progress"
        DONE = "done", "Done"
        CANCELLED = "cancelled", "Cancelled"

    class TaskPriority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    user = models.ForeignKey(
        "auth.user",
        on_delete=models.CASCADE,
        related_name="study_tasks",
    )
    subject = models.ForeignKey(
        "subject.Subject",
        on_delete=models.CASCADE,
        related_name="study_tasks",
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    task_type = models.CharField(
        max_length=20,
        choices=TaskType.choices,
        default=TaskType.OTHER,
    )
    task_status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.TODO,
    )
    task_priority = models.CharField(
        max_length=20,
        choices=TaskPriority.choices,
        default=TaskPriority.MEDIUM,
    )
    estimated_minutes = models.PositiveIntegerField()
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
