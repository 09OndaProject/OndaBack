from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Area(models.Model):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    depth = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Interest(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, null=True, blank=True, on_delete=models.SET_NULL)
    interest = models.ForeignKey(Interest, null=True, blank=True, on_delete=models.SET_NULL)
    file = models.ForeignKey('File', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    file = models.ForeignKey('File', on_delete=models.CASCADE)

class File(models.Model):
    file = models.FileField(upload_to='uploads/')  # 실파일경로
    file_type = models.CharField(max_length=10)
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)