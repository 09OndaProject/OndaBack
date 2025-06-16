from chat.models import GroupChatRoom
from rest_framework import serializers


class GroupChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupChatRoom
        fields = ["id", "meet", "created_at"]
