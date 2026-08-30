from django.shortcuts import render
from django_filters import rest_framework as filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .filters import StudyTaskFilter
from .models import StudyTask
from .serializers import StudyTaskSerializer


# Create your views here.
class StudyTaskViewSet(ModelViewSet):
    queryset = StudyTask.objects.all()
    serializer_class = StudyTaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = StudyTaskFilter

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
