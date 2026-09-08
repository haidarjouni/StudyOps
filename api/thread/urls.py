from django.urls import path

from .views import ThreadListCreateView

urlpatterns = [
    path("", ThreadListCreateView.as_view(), name="thread-list-create"),
]