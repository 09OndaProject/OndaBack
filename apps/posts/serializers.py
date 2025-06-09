from rest_framework import serializers

from .models import Post, PostImage


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ["id", "file"]


class PostSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source="user.nickname", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "category",
            "area",
            "interest",
            "file",
            "created_at",
            "updated_at",
            "nickname",
        ]
