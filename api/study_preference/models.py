import zoneinfo

from django.db import models


def get_timezone_choices():
    # Dynamically generates a tuple list of available system timezones
    return [(tz, tz) for tz in sorted(zoneinfo.available_timezones())]


# Create your models here.
class StudyPreference(models.Model):
    user = models.OneToOneField(
        "auth.user",
        on_delete=models.CASCADE,
        related_name="study_preferences",
        primary_key=True,
    )
    timezone = models.CharField(
        max_length=64,
        choices=get_timezone_choices,  # Passes the function to keep migrations clean
        default="UTC",
    )
    earliest_study_time = models.TimeField()
    latest_study_time = models.TimeField()
    preferred_session_minutes = models.PositiveIntegerField()
    buffer_minutes = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
