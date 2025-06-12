from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from apps.leaders.models import LeaderApplication
from apps.leaders.serializers import (
    LeaderApplicationCreateSerializer,
    LeaderApplicationDetailSerializer,
    LeaderApplicationListSerializer,
    LeaderApplicationStatusUpdateSerializer,
)


# 리더 신청 + 신청 목록 조회 통합
class LeaderApplicationListCreateView(generics.ListCreateAPIView):
    # GET 관리자 전용 신청 목록 전체 조회
    # POST 일반 사용자 리더 신청 접수
    queryset = LeaderApplication.objects.all().order_by("-created_at")

    def get_permissions(self):
        # POST: 인증된 사용자만 신청 가능
        # GET: 관리자만 신청 목록 조회 가능
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def get_serializer_class(self):
        # POST 요청시 생성용 직렬화 , GET 요청시 목록 직렬화
        if self.request.method == "POST":
            return LeaderApplicationCreateSerializer
        return LeaderApplicationListSerializer

    def perform_create(self, serializer):
        # 신청서 저장 시 현재 로그인 사용자와 연결
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        tags=["리더신청"],
        operation_summary="리더 신청 (일반 사용자)",
        operation_description="일반 사용자가 리더 신청을 보냅니다.",
        request_body=LeaderApplicationCreateSerializer,
        responses={201: LeaderApplicationCreateSerializer},
    )
    def post(self, request, *args, **kwargs):
        # 동일 사용자의 중복 신청 방지
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
    # GET 신청서 ID로상세 조회 (괄리자만 접근 가능)
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
    # PATCH 신청 산태 승인/거절 처리 (관리자 전용)
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
        # 승인된 경우 사용자 role 업데이트
        instance = self.get_object()
        if instance.status == "approved":
            user = instance.user
            user.role = 2  # leader
            user.save()
        return response
