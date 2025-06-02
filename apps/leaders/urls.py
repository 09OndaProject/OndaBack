from django.urls import path
from apps.leaders.views import (
    LeaderApplicationListCreateView,
    LeaderApplicationDetailView,
    LeaderApplicationStatusUpdateView,
)

urlpatterns = [
    path("apply", LeaderApplicationListCreateView.as_view()),              # GET (관리자), POST (일반 유저)
    path("apply/<int:pk>", LeaderApplicationDetailView.as_view()),        # GET (관리자)
    path("apply/<int:pk>/status", LeaderApplicationStatusUpdateView.as_view()),  # PATCH (관리자)
]
