from rest_framework import routers

from study_task.views import StudyTaskViewSet

router = routers.DefaultRouter()

router.register("", StudyTaskViewSet, basename="studytask")

urlpatterns = router.urls
