from rest_framework import generics, permissions, filters
from .models import Post
from .serializers import PostSerializer
from rest_framework.exceptions import PermissionDenied

class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']

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
