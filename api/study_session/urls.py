from rest_framework import routers

from .views import StudySessionViewSet

router = routers.DefaultRouter()

router.register("", StudySessionViewSet, basename="study_session")

urlpatterns = router.urls
