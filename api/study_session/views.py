from django_filters import rest_framework as filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .filters import StudySessionFilter
from .models import StudySession
from .serializers import StudySessionSerializer


class StudySessionViewSet(ModelViewSet):
    serializer_class = StudySessionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = StudySessionFilter

    def get_queryset(self):
        return (
            StudySession.objects.filter(user=self.request.user)
            .select_related("subject", "task")
            .order_by("-start_at")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
