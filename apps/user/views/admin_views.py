from django.contrib.auth import get_user_model
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.user.models import UserRole
from apps.user.serializers.admin_serializers import (
    AdminUserCreateSerializer,
    AdminUserListSerializer,
    AdminUserProfileSerializer,
    AdminUserProfileUpdateSerializer,
)
from utils.pagination import CustomPageNumberPagination

User = get_user_model()


class AdminUserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AdminUserListSerializer
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]  # JWT 인증
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action == "list":
            return AdminUserListSerializer
        if self.action == "create":
            return AdminUserCreateSerializer
        if self.action == "retrieve":
            return AdminUserProfileSerializer
        if self.action == "partial_update":
            return AdminUserProfileUpdateSerializer

        return super().get_serializer_class()

    def get_queryset(self):

        if self.action == "list":
            queryset = User.objects.select_related(
                "area", "area__parent", "area__parent__parent", "digital_level", "file"
            ).prefetch_related("interests")
            query = self.request.query_params
            q = Q()

            # :=는 Python 3.8 이상에서 도입된 **"월러스 연산자 (walrus operator)"**입니다.
            # 이 연산자는 할당과 동시에 표현식 안에서 변수 사용이 가능하게 해줍니다.

            if email := query.get("email"):
                q &= Q(email__icontains=email)  # 부분 일치 검색

            if name := query.get("name"):
                q &= Q(name__icontains=name)

            if nickname := query.get("nickname"):
                q &= Q(nickname__icontains=nickname)

            if phone_number := query.get("phone_number"):
                q &= Q(phone_number__icontains=phone_number)

            if date_of_birth := query.get("date_of_birth"):
                q &= Q(date_of_birth=date_of_birth)  # 정확 일치

            if area := query.get("area"):
                q &= (
                    Q(area__id=area)
                    | Q(area__parent__id=area)
                    | Q(area__parent__parent__id=area)
                )  # 외래키 이름 검색 가정

            if interest := query.get("interest"):
                q &= Q(interests__id=interest)

            if digital_level := query.get("digital_level"):
                q &= Q(digital_level__id=digital_level)

            if role := query.get("role"):
                try:
                    role_value = UserRole[role.upper()].value
                    q &= Q(role=role_value)
                except KeyError:
                    pass

            if is_deleted := query.get("is_deleted"):
                is_deleted = True if is_deleted.lower() == "true" else False
                q &= Q(is_deleted=is_deleted)
            else:
                q &= Q(is_deleted=False)

            return queryset.filter(q).order_by("-created_at")

        elif self.action == "retrieve":
            return User.objects.select_related(
                "area", "area__parent", "area__parent__parent", "digital_level", "file"
            ).prefetch_related("interests")

        else:
            return self.queryset

    @swagger_auto_schema(
        tags=["관리자/유저"],
        operation_summary="유저 목록",
        manual_parameters=[
            openapi.Parameter(
                "email",
                openapi.IN_QUERY,
                description="이메일",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "name", openapi.IN_QUERY, description="이름", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                "nickname",
                openapi.IN_QUERY,
                description="닉네임",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "phone_number",
                openapi.IN_QUERY,
                description="전화번호",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "date_of_birth",
                openapi.IN_QUERY,
                description="생년월일",
                type=openapi.TYPE_STRING,
                format="date",
            ),
            openapi.Parameter(
                "role",
                openapi.IN_QUERY,
                description="유저 역할(admin, user, leader)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "area",
                openapi.IN_QUERY,
                description="지역 ID",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "digital_level",
                openapi.IN_QUERY,
                description="디지털 레벨 ID",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "is_deleted",
                openapi.IN_QUERY,
                description="삭제된 사용자 표시",
                type=openapi.TYPE_STRING,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["관리자/유저"],
        operation_summary="유저 생성",
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["관리자/유저"],
        operation_summary="유저 상세",
    )
    def retrieve(self, request, *args, **kwargs):
        """
        유저의 모든 정보를 표시 (비밀번호 제외)
        """
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def update(self, request, *args, **kwargs):
        # PUT 요청 (전체 수정)만 차단
        if not kwargs.get("partial", False):
            raise MethodNotAllowed("PUT")

        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["관리자/유저"],
        operation_summary="유저 정보 일부 수정",
    )
    def partial_update(self, request, *args, **kwargs):
        """
        유저의 권한, 활성화 여부만 수정 가능
        """
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["관리자/유저"],
        operation_summary="유저 삭제",
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
