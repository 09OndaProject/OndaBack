from django.urls import path

from .views import *

app_name = "meet"

urlpatterns = [
    path("", MeetListCreateView.as_view()),
    path("apply/<int:meet_id>", MeetApplyView.as_view()),
    path("<int:meet_id>", MeetRetrieveUpdateDestroyView.as_view()),
    path("users/<int:user_id>/", MeetUserListView.as_view(), name="user-meet-list"),
]
