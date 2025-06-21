from django.urls import path

from apps.chat.views import GroupChatMessageListView

from .views import JoinGroupChatView

urlpatterns = [
    path(
        "group-chat/join/<int:meet_id>",
        JoinGroupChatView.as_view(),
        name="group-chat-join",
    ),
    path("group-chat/<int:room_id>/messages", GroupChatMessageListView.as_view()),
]
