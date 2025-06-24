from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.meet.models import Meet, MeetApply

from .models import Review


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["rating", "content"]

    def validate(self, data):
        user = self.context["request"].user
        meet_id = self.context["view"].kwargs["meet_id"]
        meet = get_object_or_404(Meet, id=meet_id, is_deleted=False)

        if not MeetApply.objects.filter(user=user, meet=meet).exists():
            raise ValidationError("이 모임에 참가하지 않았습니다.")

        if meet.date:
            now = timezone.now().date()
            if now < meet.date:
                raise ValidationError("모임이 종료된 후에만 리뷰를 작성할 수 있습니다.")
            if now > meet.date + timedelta(days=14):
                raise ValidationError("모임 종료 후 14일이 지나 작성할 수 없습니다.")

        if Review.objects.filter(user=user, meet=meet).exists():
            raise ValidationError("이미 리뷰를 작성하셨습니다.")

        return data


class ReviewDisplaySerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source="user.nickname", read_only=True)
    meet_title = serializers.CharField(source="meet.title", read_only=True)
    meet_date = serializers.DateField(source="meet.date", read_only=True)
    meet_location = serializers.CharField(source="meet.location", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "nickname",
            "rating",
            "content",
            "created_at",
            "meet_title",
            "meet_date",
            "meet_location",
        ]
