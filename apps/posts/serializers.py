from rest_framework import serializers

from .models import Comment, Like, Post, PostImage


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ["id", "file"]


class PostSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source="user.nickname", read_only=True)
    like_count = serializers.IntegerField(source="likes.count", read_only=True)
    is_liked = serializers.SerializerMethodField()

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
            "like_count",
            "is_liked",
        ]

        def get_is_mine(self, obj):
            # context에 request가 있어야 함 (APIView에서 serializer에 전달됨)
            request = self.context.get('request')
            return request and request.user.is_authenticated and obj.user == request.user

        def get_is_liked(self, obj):
            request = self.context.get("request")
            if not request or not request.user.is_authenticated:
                return False
            return obj.likes.filter(user=request.user).exists()


class RecursiveField(serializers.Serializer):
    """대댓글 구조(트리) 직렬화용"""
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class CommentSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source="user.nickname", read_only=True)
    is_mine = serializers.SerializerMethodField()
    replies = RecursiveField(many=True, read_only=True)  # 대댓글들

    class Meta:
        model = Comment
        fields = [
            "id", "post", "user", "nickname",
            "content", "parent", "created_at", "updated_at",
            "is_mine", "replies"
        ]
        read_only_fields = ("user", "nickname", "created_at", "updated_at", "is_mine", "replies")

    def get_is_mine(self, obj):
        request = self.context.get("request")
        return request and request.user.is_authenticated and obj.user == request.user

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        return Comment.objects.create(user=user, **validated_data)

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["id", "user", "post", "created_at"]
        read_only_fields = ("user", "created_at")