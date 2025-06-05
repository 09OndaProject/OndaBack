from django.conf import settings
from django.shortcuts import get_object_or_404, render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    UpdateModelMixin,
)
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import File
from .serializers import FileSerializer

# def file_manager_view(request):
#     return render(request, "file_manager.html")


# listview test
class FileListUploadView(ListCreateAPIView):
    queryset = File.objects.all()
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 데이터 접근 가능
    authentication_classes = [JWTAuthentication]  # JWT 인증
    serializer_class = FileSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        if self.request.method == "GET":
            return self.queryset.filter(user=self.request.user)
        return super().get_queryset()

    @swagger_auto_schema(
        tags=["업로드"],
        operation_summary="업로드 파일 리스트 반환",
        operation_description="",
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["업로드"],
        operation_summary="파일 업로드",
        operation_description="",
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class FileUpdateDeleteView(UpdateModelMixin, DestroyModelMixin, GenericAPIView):
    queryset = File.objects.all()
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 데이터 접근 가능
    authentication_classes = [JWTAuthentication]  # JWT 인증
    serializer_class = FileSerializer
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        tags=["업로드"],
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["업로드"],
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        id = instance.id
        self.perform_destroy(instance)
        return Response(
            {"message": "삭제 성공", "id": id}, status=status.HTTP_204_NO_CONTENT
        )
