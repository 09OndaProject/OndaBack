from django.urls import path
from .views import JoinGroupChatView

urlpatterns = [
    path('group-chat/join/<int:meet_id>/', JoinGroupChatView.as_view(), name='group-chat-join'),
]