from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema

from apps.leaders.models import LeaderApplication
from apps.leaders.serializers import (
    LeaderApplicationCreateSerializer,
    LeaderApplicationListSerializer,
    LeaderApplicationDetailSerializer,
    LeaderApplicationStatusUpdateSerializer,
)


# 리더 신청 + 신청 목록 조회 통합
class LeaderApplicationListCreateView(generics.ListCreateAPIView):
    queryset = LeaderApplication.objects.all().order_by("-created_at")

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return LeaderApplicationCreateSerializer
        return LeaderApplicationListSerializer

    @swagger_auto_schema(
        tags=["리더신청"],
        operation_summary="리더 신청 (일반 사용자)",
        operation_description="일반 사용자가 리더 신청을 보냅니다.",
        request_body=LeaderApplicationCreateSerializer,
        responses={201: LeaderApplicationCreateSerializer},
    )
    def post(self, request, *args, **kwargs):
        if LeaderApplication.objects.filter(user=request.user).exists():
            raise PermissionDenied("이미 신청한 이력이 있습니다.")
        return self.create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["리더신청"],
        operation_summary="리더 신청 목록 조회 (관리자)",
        operation_description="관리자 전용 신청 목록 전체 조회",
        responses={200: LeaderApplicationListSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


# 신청 상세 조회 (관리자 전용)
class LeaderApplicationDetailView(generics.RetrieveAPIView):
    serializer_class = LeaderApplicationDetailSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = LeaderApplication.objects.all()

    @swagger_auto_schema(
        tags=["리더신청"],
        operation_summary="리더 신청 상세 조회",
        operation_description="신청서 ID로 상세 조회 (관리자만 접근 가능)",
        responses={200: LeaderApplicationDetailSerializer},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


# 승인 / 거절 처리 (관리자 전용)
class LeaderApplicationStatusUpdateView(generics.UpdateAPIView):
    serializer_class = LeaderApplicationStatusUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = LeaderApplication.objects.all()

    @swagger_auto_schema(
        tags=["리더신청"],
        operation_summary="리더 신청 승인/거절 처리",
        operation_description="관리자가 신청서 상태를 승인 또는 거절 처리합니다.",
        request_body=LeaderApplicationStatusUpdateSerializer,
        responses={200: LeaderApplicationStatusUpdateSerializer},
    )
    def patch(self, request, *args, **kwargs):
        response = self.partial_update(request, *args, **kwargs)
        instance = self.get_object()
        if instance.status == "approved":
            user = instance.user
            user.role = 2  # leader
            user.save()
        return response
