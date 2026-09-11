from django.db import transaction
from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from study_session.models import StudySession
from study_session.serializers import StudySessionSerializer

from .filters import StudyTaskFilter
from .models import StudyTask
from .schedule_serializers import ScheduleCreateSerializer
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

    @action(detail=False, methods=["post"], url_path="schedule")
    def create_schedule(self, request):
        # serialized the request
        serializer = ScheduleCreateSerializer(
            data=request.data,
            # sending the context of the request to the serializer so that it can access the request user and other information
            context=self.get_serializer_context(),
        )
        # validate
        serializer.is_valid(raise_exception=True)

        # a tuple of the created task and its sessions will be appended to this list
        created_drafts = []
        with transaction.atomic():
            for draft in serializer.validated_data["drafts"]:
                # create the task object
                task = StudyTask.objects.create(
                    user=request.user,
                    **draft["task"],
                )
                # create the sessions
                sessions = [
                    StudySession.objects.create(
                        user=request.user,
                        task=task,
                        **{
                            key: value
                            for key, value in session.items()
                            if key != "task"
                        },
                    )
                    for session in draft["sessions"]
                ]
                # append them in a tuple
                created_drafts.append((task, sessions))

        serializer_context = self.get_serializer_context()
        response_data = {
            "drafts": [
                {
                    "task": StudyTaskSerializer(
                        task,
                        context=serializer_context,
                    ).data,
                    "sessions": StudySessionSerializer(
                        sessions,
                        many=True,
                        context=serializer_context,
                    ).data,
                }
                for task, sessions in created_drafts
            ]
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
