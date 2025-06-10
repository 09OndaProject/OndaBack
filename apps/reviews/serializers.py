from rest_framework import serializers

from .models import Review


class ReviewCreateSerializer(serializers.ModelSerializer):
    """리뷰 작성용 Serializer"""

    class Meta:
        model = Review
        fields = ["rating", "content"]


class ReviewDisplaySerializer(serializers.ModelSerializer):
    """리뷰 조회용 Serializer (리스트/상세 공통)"""

    user_name = serializers.CharField(source="user.username", read_only=True)
    meet_title = serializers.CharField(source="meet.title", read_only=True)
    meet_date = serializers.DateField(source="meet.date", read_only=True)  # 날짜만
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
