from django.urls import path

from apps.leaders.views import (
    LeaderApplicationDeleteView,
    LeaderApplicationDetailView,
    LeaderApplicationListCreateView,
    LeaderApplicationStatusUpdateView,
    MyLeaderApplicationDetailView,
)

urlpatterns = [
    path(
        "leader-applis",
        LeaderApplicationListCreateView.as_view(),
    ),  # GET (관리자), POST (일반 유저)
    path(
        "leader-applis/<int:pk>", LeaderApplicationDetailView.as_view()
    ),  # GET (관리자)
    path(
        "leader-applis/<int:pk>/status", LeaderApplicationStatusUpdateView.as_view()
    ),  # PATCH (관리자)
    path(
        "leader-applyis/<int:pk>/delete",
        LeaderApplicationDeleteView.as_view(),
    ),
    path(
        "leader-applis/mine",
        MyLeaderApplicationDetailView.as_view(),
    ),
]
