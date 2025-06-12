from rest_framework import serializers

from .models import Post, PostImage


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ["id", "file"]


class PostSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source="user.nickname", read_only=True)
    is_mine = serializers.BooleanField(read_only=True)

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
            "is_mine",
        ]

        def get_is_mine(self, obj):
            # context에 request가 있어야 함 (APIView에서 serializer에 전달됨)
            request = self.context.get("request")
            return (
                request and request.user.is_authenticated and obj.user == request.user
            )
