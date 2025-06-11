from django.utils import timezone
from rest_framework import serializers

from .models import Meet, MeetApply


class MeetSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source="user.nickname", read_only=True)

    class Meta:
        model = Meet
        fields = [
            "id",
            "title",
            "description",
            "area",
            "digital_level",
            "interest",
            "date",
            "time",
            "location",
            "contact",
            "max_people",
            "current_people",
            #"file",
            "status",
            "application_deadline",
            "created_at",
            "user_nickname",
        ]
        read_only_fields = ["status", "current_people", "created_at", "user_nickname"]


class MeetDetailSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source="user.nickname", read_only=True)

    class Meta:
        model = Meet
        fields = "__all__"
        read_only_fields = [
            "user",
            "status",
            "current_people",
            "created_at",
            "updated_at",
            "user_nickname",
        ]
