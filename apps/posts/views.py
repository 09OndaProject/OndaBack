from rest_framework import filters, generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment, Like, Post
from .serializers import CommentSerializer, PostSerializer


class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "content"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        # 본인만 수정/삭제 가능 로직 필요
        if self.request.user != self.get_object().user:
            raise PermissionDenied("권한이 없습니다.")
        serializer.save()

class CommentListCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.filter(parent=None).order_by("-created_at")  # 최상위 댓글만
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # 특정 게시글(post_id)에 대한 댓글만
        post_id = self.kwargs["post_id"]
        return Comment.objects.filter(post_id=post_id, parent=None).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, post_id=self.kwargs["post_id"])

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        if self.request.user != self.get_object().user:
            raise PermissionDenied("본인 댓글만 수정할 수 있습니다.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.user:
            raise PermissionDenied("본인 댓글만 삭제할 수 있습니다.")
        instance.delete()

class LikeToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = Post.objects.get(pk=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            # 이미 좋아요 되어있으면 취소
            like.delete()
            return Response({"liked": False, "like_count": post.likes.count()})
        return Response({"liked": True, "like_count": post.likes.count()})