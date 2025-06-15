from django.urls import path

from apps.leaders.views import (
    LeaderApplicationDetailView,
    LeaderApplicationListCreateView,
    LeaderApplicationStatusUpdateView,
)

urlpatterns = [
    path(
        "leader-applies", LeaderApplicationListCreateView.as_view()
    ),  # GET (관리자), POST (일반 유저)
    path(
        "leader-applies/<int:pk>", LeaderApplicationDetailView.as_view()
    ),  # GET (관리자)
    path(
        "leader-applies/<int:pk>/status", LeaderApplicationStatusUpdateView.as_view()
    ),  # PATCH (관리자)
]
