from django.urls import path

from .views import *

app_name = "meet"

urlpatterns = [
    path("meets", MeetListCreateView.as_view()),
    path("meets/apply/<int:meet_id>", MeetApplyView.as_view()),
    path("meets/<int:meet_id>", MeetRetrieveUpdateDestroyView.as_view()),
    path(
        "meets/users/<int:user_id>", MeetUserListView.as_view(), name="user-meet-list"
    ),
]
