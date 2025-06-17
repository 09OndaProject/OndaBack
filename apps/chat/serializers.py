from rest_framework import serializers

from apps.chat.models import GroupChatRoom


class GroupChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupChatRoom
        fields = ["id", "meet", "created_at"]
