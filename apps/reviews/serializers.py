from rest_framework import serializers

from .models import Review


# 리뷰 작성용 Serializer
class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["rating", "content"]


# 리뷰 목록 및 상세 조회용 공통 Serializer
class ReviewDisplaySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    meet_title = serializers.CharField(source="meet.title", read_only=True)
    meet_date = serializers.DateTimeField(source="meet.date", read_only=True)
    meet_location = serializers.CharField(source="meet.location", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "user_name",
            "rating",
            "content",
            "created_at",
            "meet_title",
            "meet_date",
            "meet_location",
        ]
