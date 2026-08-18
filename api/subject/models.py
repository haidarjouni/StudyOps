from django.db import models


# Create your models here.
class Subject(models.Model):
    user = models.ForeignKey(
        "auth.user",
        on_delete=models.CASCADE,
        related_name="subjects",
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    semester = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
