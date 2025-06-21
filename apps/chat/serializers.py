from rest_framework import serializers

from apps.chat.models import GroupChatMessage, GroupChatRoom


class GroupChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupChatRoom
        fields = ["id", "meet", "created_at"]


class GroupChatMessageSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    nickname = serializers.CharField(source="user.nickname", read_only=True)
    created_at = serializers.DateTimeField(read_only=True)  # TimestampModel에서 상속됨

    class Meta:
        model = GroupChatMessage
        fields = ["id", "user_id", "nickname", "content", "created_at"]
