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
from apps.user.models import UserRole


# 리더 신청 목록 조회 및 신청 생성
# GET: 관리자만 신청 목록 전체 조회 가능
# POST: 일반 사용자가 본인의 신청서 작성 가능
class LeaderApplicationListCreateView(generics.ListCreateAPIView):
    queryset = LeaderApplication.objects.all().order_by(
        "-created_at"
    )  # 신청서 최신순 정렬

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]  # 로그인 사용자만 신청 가능
        return [permissions.IsAdminUser()]  # 관리자만 목록 조회 가능

    def get_serializer_class(self):
        if self.request.method == "POST":
            return LeaderApplicationCreateSerializer
        return LeaderApplicationListSerializer

    def perform_create(self, serializer):
        # 현재 로그인한 사용자를 신청자(user)로 저장
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        tags=["리더신청"],
        operation_summary="리더 신청 (일반 사용자)",
        operation_description="일반 사용자가 리더 신청을 보냅니다.",
        request_body=LeaderApplicationCreateSerializer,
        responses={201: LeaderApplicationCreateSerializer},
    )
    def post(self, request, *args, **kwargs):
        # 한 번만 신청 가능하도록 중복 신청 방지
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


# 리더 신청 상세 조회 (관리자 전용)
# 신청서 ID로 특정 신청서 조회
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


# 리더 신청 상태 변경 (승인/거절)
class LeaderApplicationStatusUpdateView(generics.UpdateAPIView):
    serializer_class = LeaderApplicationStatusUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = LeaderApplication.objects.all()
    http_method_names = ["patch"]  # PATCH만 허용

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

        # 상태가 approved일 경우, 사용자 권한을 리더로 변경
        if instance.status == "approved":
            user = instance.user
            user.role = UserRole.LEADER.value  # 안전하게 숫자로 저장
            user.save()
        return response


# 본인 신청서 삭제 (인증 사용자 전용)
# 로그인한 사용자가 본인 신청서를 삭제
class LeaderApplicationDeleteView(generics.DestroyAPIView):
    serializer_class = None  # 별도 응답 데이터 없음
    permission_classes = [permissions.IsAuthenticated]
    queryset = LeaderApplication.objects.all()

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):  # Swagger UI용 예외 처리
            return LeaderApplication.objects.none()
        return self.queryset.filter(user=self.request.user)  # 본인 신청서만 조회 가능

    @swagger_auto_schema(
        tags=["리더신청"],
        operation_summary="리더 신청 삭제 (본인)",
        operation_description="본인이 제출한 리더 신청서를 삭제합니다.",
        responses={204: "삭제 성공", 403: "권한 없음", 404: "존재하지 않음"},
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


# 본인 신청서 상세 조회 (사용자용)
# 로그인한 사용자의 신청서 단건 조회
class MyLeaderApplicationDetailView(generics.RetrieveAPIView):
    serializer_class = LeaderApplicationDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return LeaderApplication.objects.get(user=self.request.user)  # 본인 신청서 반환

    @swagger_auto_schema(
        tags=["리더신청"],
        operation_summary="본인 리더 신청 상세 조회",
        operation_description="로그인한 사용자의 리더 신청서를 조회합니다.",
        responses={200: LeaderApplicationDetailSerializer},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
