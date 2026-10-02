from rest_framework import routers

from .views import ThreadViewSet

router = routers.DefaultRouter()
router.register("", ThreadViewSet, basename="thread")

urlpatterns = router.urls
