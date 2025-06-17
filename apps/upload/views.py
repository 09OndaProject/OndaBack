import json

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

from .models import File
from .serializers import FileSerializer


# listview test
class FileListView(ListModelMixin, GenericAPIView):
    queryset = File.objects.all()
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 데이터 접근 가능
    authentication_classes = [JWTAuthentication]  # JWT 인증
    serializer_class = FileSerializer

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
            {"message": "업로드 성공", "ids": ids},
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

        deleted_count = 0
        for file in files:
            file.delete()
            deleted_count += 1

        return Response(
            {"message": "삭제 성공", "deleted_count": deleted_count},
            status=status.HTTP_200_OK,
        )
