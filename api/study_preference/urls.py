from django.urls import path
from study_preference.views import StudyPreferenceDetailView

urlpatterns = [
    path("me", StudyPreferenceDetailView.as_view(), name="study-preference-me")
]
