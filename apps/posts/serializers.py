from rest_framework import serializers

from apps.options.models.area import Area
from apps.options.models.category import Category
from apps.options.models.interest import Interest
from apps.upload.models import File

from .models import Comment, Like, Post, PostImage


# 1. 옵션 필드용 Serializer
class CategoryNameSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="category_name", read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name"]


class AreaNameSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="area_name", read_only=True)

    class Meta:
        model = Area
        fields = ["id", "name"]


class InterestNameSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="interest_name", read_only=True)

    class Meta:
        model = Interest
        fields = ["id", "name"]


# 2. 파일 상세용 Serializer (필요한 필드만 포함, 썸네일은 url로 반환)
class FileSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    thumbnail = serializers.ImageField()
    user_id = serializers.PrimaryKeyRelatedField(source="user", read_only=True)

    class Meta:
        model = File
        fields = [
            "id",
            "user_id",
            "file",
            "file_type",
            "file_name",
            "file_size",
            "thumbnail",
            "uploaded_at",
        ]


# 3. PostImage는 필요하면 그대로 사용
class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ["id", "file"]


# 4. PostSerializer
class PostSerializer(serializers.ModelSerializer):
    # 읽기용(응답) 직렬화
    category = CategoryNameSerializer(read_only=True)
    area = AreaNameSerializer(read_only=True)
    interest = InterestNameSerializer(read_only=True)
    file = FileSerializer(read_only=True)

    # 쓰기용(등록/수정) 필드
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
        required=True,
    )
    area_id = serializers.PrimaryKeyRelatedField(
        queryset=Area.objects.all(),
        source="area",
        write_only=True,
        required=False,
        allow_null=True,
    )
    interest_id = serializers.PrimaryKeyRelatedField(
        queryset=Interest.objects.all(),
        source="interest",
        write_only=True,
        required=False,
        allow_null=True,
    )
    file_id = serializers.PrimaryKeyRelatedField(
        queryset=File.objects.all(),
        source="file",
        write_only=True,
        required=False,
        allow_null=True,
    )

    nickname = serializers.CharField(source="user.nickname", read_only=True)
    like_count = serializers.IntegerField(source="likes.count", read_only=True)
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "category",  # 읽기
            "category_id",  # 쓰기
            "area",
            "area_id",
            "interest",
            "interest_id",
            "file",
            "file_id",
            "created_at",
            "updated_at",
            "nickname",
            "is_mine",
            "like_count",
        ]

    def get_is_mine(self, obj):
        request = self.context.get("request")
        return request and request.user.is_authenticated and obj.user == request.user

    # Create, update 시에는 id값만 받도록 override
    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        # POST/PUT/PATCH에서 category/area/interest/file의 id를 매핑
        for field, model in [
            ("category", Category),
            ("area", Area),
            ("interest", Interest),
            ("file", File),
        ]:
            val = data.get(field)
            if val:
                try:
                    ret[field] = model.objects.get(pk=val)
                except model.DoesNotExist:
                    self.fail(f"{field}_not_found")
        return ret


# 5. RecursiveField (대댓글 용)
class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


# 6. CommentSerializer
class CommentSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source="user.nickname", read_only=True)
    is_mine = serializers.SerializerMethodField()
    replies = RecursiveField(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "user",
            "nickname",
            "content",
            "parent",
            "created_at",
            "updated_at",
            "is_mine",
            "replies",
        ]
        read_only_fields = (
            "user",
            "nickname",
            "created_at",
            "updated_at",
            "is_mine",
            "replies",
            "post",
        )

    def get_is_mine(self, obj):
        request = self.context.get("request")
        return request and request.user.is_authenticated and obj.user == request.user

    def create(self, validated_data):
        user = validated_data.pop("user")
        post = validated_data.pop("post")
        return Comment.objects.create(user=user, post=post, **validated_data)


# 7. LikeSerializer
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["id", "user", "post", "created_at"]
        read_only_fields = ("user", "created_at")

    def get_is_mine(self, obj):
        request = self.context.get("request")
        return request and request.user.is_authenticated and obj.user == request.user
