from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Thread
from .serializers import ThreadSerializer

class ThreadListCreateView(generics.ListCreateAPIView):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Thread.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)