from django.conf import settings
from django.db import models

from apps.options.models.area import Area
from apps.options.models.category import Category
from apps.options.models.interest import Interest


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, null=True, blank=True, on_delete=models.SET_NULL)
    interest = models.ForeignKey(Interest, null=True, blank=True, on_delete=models.SET_NULL)
    file = models.ForeignKey("File", null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")
    file = models.ForeignKey("File", on_delete=models.CASCADE)


class File(models.Model):
    file = models.FileField(upload_to="uploads/")  # 실파일경로
    file_type = models.CharField(max_length=10)
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # 대댓글이면 부모 pk, 아니면 None
        return f"{self.user.nickname} - {self.content[:20]} ({'대댓글' if self.parent else '댓글'})"


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")  # 한 유저가 한 게시글에 한 번만 좋아요