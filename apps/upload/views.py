import json
import logging
import os

import boto3
from django.conf import settings
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView, ListCreateAPIView
from rest_framework.mixins import (
    DestroyModelMixin,
    ListModelMixin,
)
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from utils.pagination import CustomPageNumberPagination

from .models import File
from .serializers import FileSerializer

logger = logging.getLogger(__name__)


# listview test
class FileListView(ListModelMixin, GenericAPIView):
    queryset = File.objects.all()
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 데이터 접근 가능
    authentication_classes = [JWTAuthentication]  # JWT 인증
    serializer_class = FileSerializer
    pagination_class = CustomPageNumberPagination

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


class FileUploadView(CreateAPIView):
    queryset = File.objects.all()
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 데이터 접근 가능
    authentication_classes = [JWTAuthentication]  # JWT 인증
    serializer_class = FileSerializer
    parser_classes = [MultiPartParser, FormParser]

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
        files = self.perform_create(serializer)

        # 새 직렬화기로 many=True 적용
        response_serializer = FileSerializer(
            files, many=True, context={"request": request}
        )

        # headers는 첫 번째 객체로부터 생성
        headers = self.get_success_headers(
            response_serializer.data[0] if response_serializer.data else None
        )

        # id만 추출하여 응답
        ids = [file["id"] for file in response_serializer.data]

        return Response(
            {"message": "파일 업로드를 성공했습니다.", "ids": ids},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer):
        return serializer.save()


class FileDeleteView(DestroyModelMixin, GenericAPIView):
    queryset = File.objects.all()
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 데이터 접근 가능
    authentication_classes = [JWTAuthentication]  # JWT 인증
    serializer_class = FileSerializer

    @swagger_auto_schema(
        tags=["업로드"],
        operation_summary="파일 삭제",
        operation_description="ids 리스트를 받아 여러 파일을 삭제합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["ids"],
            properties={
                "ids": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_INTEGER),
                    description="삭제할 파일 ID 리스트",
                )
            },
            example={"ids": [125, 126]},
        ),
        responses={
            200: openapi.Response(
                description="삭제 성공",
                examples={
                    "application/json": {"message": "삭제 성공", "deleted_count": 2}
                },
            ),
            400: openapi.Response(
                description="잘못된 요청",
                examples={"application/json": {"detail": "List of IDs expected."}},
            ),
        },
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            ids = data.get("ids", [])
        except json.JSONDecodeError:
            return Response({"detail": "Invalid JSON."}, status=400)

        if not isinstance(ids, list):
            return Response({"detail": "List of IDs expected."}, status=400)

        files = File.objects.filter(id__in=ids)
        deleted_count = files.count()

        if settings.DJANGO_ENV == "prod":
            # S3 클라이언트 초기화
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )

            # S3 버킷 이름
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME

            # 삭제할 파일 키 목록
            delete_objects = []

            # 파일과 썸네일의 S3 키 수집
            for file in files:
                if file.file:
                    file_key = f"{file.file.storage.location}/{file.file.name}"
                    delete_objects.append({"Key": file_key})

                if file.thumbnail:
                    thumbnail_key = (
                        f"{file.thumbnail.storage.location}/{file.thumbnail.name}"
                    )
                    delete_objects.append({"Key": thumbnail_key})

            # S3에서 일괄 삭제 (최대 1000개까지 한 번에 삭제 가능)
            if delete_objects:
                # 1000개씩 나누어서 처리
                for i in range(0, len(delete_objects), 1000):
                    try:
                        s3_client.delete_objects(
                            Bucket=bucket_name,
                            Delete={"Objects": delete_objects[i : i + 1000]},
                        )
                    except Exception as e:
                        logger.exception("S3 삭제 중 오류 발생")
        else:
            for file in files:
                # 파일 시스템에서 실제 파일들 삭제
                file.delete(soft=False)

        # 데이터베이스에서 한 번에 삭제
        files.delete()

        return Response(
            {"message": "파일 삭제를 성공했습니다.", "deleted_count": deleted_count},
            status=status.HTTP_200_OK,
        )


# files = File.objects.filter(...)	❌ 쿼리 미실행
# files.count()	✅ 즉시 실행
# len(files)	✅ 즉시 실행
# for file in files:	✅ 즉시 실행
# list(files)	✅ 즉시 실행
# files.exists()	✅ 즉시 실행
