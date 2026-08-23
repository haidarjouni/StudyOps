from django.contrib import admin
from django.urls import path
from rest_framework import routers

from subject.views import SubjectView
router = routers.DefaultRouter()

router.register('', SubjectView, basename='subject')

urlpatterns = router.urls