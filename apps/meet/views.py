# meet/views.py
from django.db.models import F
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.options.models import Area
from utils.permissions import IsOwnerOrReadOnly, LeaderOnly

from .models import Meet, MeetApply
from .serializers import (
    MeetCreateSerializer,
    MeetDetailSerializer,
    MeetListSerializer,
    MeetUpdateSerializer,
    MeetUserListSerializer,
)


# /api/meets [GET, POST]
class MeetListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == "POST":
            return MeetCreateSerializer
        return MeetListSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), LeaderOnly()]
        return [IsAuthenticatedOrReadOnly()]

    @swagger_auto_schema(
        tags=["모임"],
        operation_summary="모임 목록 조회",
        manual_parameters=[
            openapi.Parameter(
                "title",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="모임 제목",
            ),
            openapi.Parameter(
                "area",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="지역",
            ),
            openapi.Parameter(
                "category",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="카테고리",
            ),
            openapi.Parameter(
                "digital_level",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="디지털 수준",
            ),
        ],
        responses={200: MeetListSerializer(many=True)},
    )
    def get_all_descendant_area_ids(self, area, visited=None):
        if visited is None:
            visited = set()

        if area.id in visited:
            return []

        visited.add(area.id)
        result = [area.id]

        for child in area.children.all():
            result += self.get_all_descendant_area_ids(child, visited)

        return result

    def get_queryset(self):
        queryset = Meet.objects.select_related("area", "file", "user").order_by(
            "-created_at"
        )
        title = self.request.query_params.get("title")
        area_id = self.request.query_params.get("area")
        category = self.request.query_params.get("category")
        digital_level = self.request.query_params.get("digital_level")

        if title:
            queryset = queryset.filter(title__icontains=title)

        if area_id:
            try:
                area = Area.objects.prefetch_related("children").get(id=area_id)
                area_ids = self.get_all_descendant_area_ids(area)
                queryset = queryset.filter(area_id__in=area_ids)
            except Area.DoesNotExist:
                queryset = queryset.none()

        if category:
            queryset = queryset.filter(category=category)

        if digital_level:
            queryset = queryset.filter(digital_level=digital_level)

        return queryset

    @swagger_auto_schema(
        tags=["모임"],
        operation_summary="모임 등록",
        request_body=MeetCreateSerializer,
        responses={
            201: openapi.Response(
                description="모임 생성 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="모임 생성이 완료 되었습니다",
                        ),
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                    },
                ),
            ),
            400: "잘못된 요청",
            403: "권한 없음",
        },
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        meet = serializer.save(user=request.user)
        return Response(
            {"message": "모임 생성이 완료 되었습니다", "id": meet.id},
            status=status.HTTP_201_CREATED,
        )


# /api/meets/{meet_id} [GET, PATCH, DELETE]
class MeetRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Meet.objects.select_related(
        "user", "file", "category", "digital_level"
    ).prefetch_related("applications__user__file")
    lookup_url_kwarg = "meet_id"
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return MeetUpdateSerializer
        return MeetDetailSerializer

    @swagger_auto_schema(
        tags=["모임"],
        operation_summary="모임 상세 조회",
        responses={200: MeetDetailSerializer()},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["모임"],
        operation_summary="모임 부분 수정",
        request_body=MeetUpdateSerializer,
        responses={
            200: openapi.Response(
                description="모임 수정 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="모임 수정이 완료 되었습니다",
                        ),
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                    },
                ),
            ),
            400: "잘못된 요청",
            403: "권한 없음",
        },
    )
    def patch(self, request, *args, **kwargs):
        meet = self.get_object()

        if meet.user != request.user:
            raise PermissionDenied("모임을 수정할 권한이 없습니다.")

        serializer = self.get_serializer(meet, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "모임 수정이 완료 되었습니다", "id": meet.id},
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        tags=["모임"],
        operation_summary="모임 삭제 (soft delete)",
        responses={
            204: "모임 삭제 성공",
            403: "권한 없음",
        },
    )
    def delete(self, request, *args, **kwargs):
        meet = self.get_object()
        if meet.user != request.user:
            raise PermissionDenied("모임을 삭제할 권한이 없습니다.")
        self.perform_destroy(meet)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


# /api/meets/aply/{meet_id} [POST]
class MeetApplyView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["모임"],
        operation_summary="모임 지원",
        responses={
            201: openapi.Response(
                description="모임 지원 완료",
                examples={
                    "application/json": {"detail": "모임 지원이 완료되었습니다."}
                },
            ),
            400: openapi.Response(description="지원 실패 (중복 지원 또는 모집 마감)"),
        },
    )
    def post(self, request, meet_id):
        meet = get_object_or_404(Meet, pk=meet_id)

        if MeetApply.objects.filter(user=request.user, meet=meet).exists():
            return Response(
                {"detail": "이미 지원한 모임입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if meet.status != "모집중":
            return Response(
                {"detail": "모집이 종료된 모임입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        MeetApply.objects.create(user=request.user, meet=meet)
        meet.current_people = F("current_people") + 1
        meet.save()
        meet.refresh_from_db()
        return Response(
            {"detail": "모임 지원이 완료되었습니다."}, status=status.HTTP_201_CREATED
        )


# /api/meets/users/{user_id} [GET]
class MeetUserListView(generics.ListAPIView):
    serializer_class = MeetUserListSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["모임"],
        operation_summary="사용자 모임 목록 조회",
        responses={200: MeetUserListSerializer(many=True)},
    )
    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        queryset = Meet.objects.select_related("area").filter(user_id=user_id)
        return queryset
