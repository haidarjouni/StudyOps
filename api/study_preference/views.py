from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from .serializers import StudyPreferenceSerializer


class StudyPreferenceDetailView(RetrieveUpdateAPIView):
    serializer_class = StudyPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.study_preferences
