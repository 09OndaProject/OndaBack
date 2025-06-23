from django.urls import path

from .views import *

app_name = "meet"

urlpatterns = [
    path("meets", MeetListCreateView.as_view()),
    path("meets/apply/<int:meet_id>", MeetApplyView.as_view()),
    path("meets/<int:meet_id>", MeetRetrieveUpdateDestroyView.as_view()),
    path(
        "meets/leaders/<int:leader_id>",
        MeetLeaderListView.as_view(),
        name="leader-meet-list",
    ),
    path("meets/users", MeetUserListView.as_view(), name="user-meet-list"),
]
