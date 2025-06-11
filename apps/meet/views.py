# meet/views.py
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import F
from .models import Meet, MeetApply
from .serializers import MeetDetailSerializer, MeetSerializer
from utils.permissions import IsOwnerOrReadOnly
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


# /api/meets [GET, POST]
class MeetListCreateView(generics.ListCreateAPIView):
    serializer_class = MeetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @swagger_auto_schema(
        operation_summary="모임 목록 조회",
        manual_parameters=[
            openapi.Parameter("title", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="모임 제목"),
            openapi.Parameter("area", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="지역"),
            openapi.Parameter("interest", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="관심사"),
            openapi.Parameter("digital_level", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="디지털 수준"),
        ]
    )
        
    def get_queryset(self):
        queryset = Meet.objects.all().order_by("-created_at")
        title = self.request.query_params.get("title")
        area = self.request.query_params.get("area")
        interest = self.request.query_params.get("interest")
        digital_level = self.request.query_params.get("digital_level")
        
        if title:
            queryset = queryset.filter(title__icontains=title)
        if area:
            queryset = queryset.filter(area=area)
        if interest:
            queryset = queryset.filter(interest=interest)
        if digital_level:
            queryset = queryset.filter(digitalLevel=digital_level)
        return queryset
    
    @swagger_auto_schema(
        operation_summary="모임 등록",
        request_body=MeetSerializer,
        responses={201: openapi.Response("Created", openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING),
                'id': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        ))}
    )

    def create(self, request, *args, **kwargs):
        if request.user.role != 2:
            raise PermissionDenied("모임을 생성할 권한이 없습니다.")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        meet = serializer.save(user=request.user)
        return Response({"message": "모임 생성이 완료 되었습니다", "id": meet.id}, status=status.HTTP_201_CREATED)
    
# /api/meets/{meet_id} [GET, PATCH, DELETE]
class MeetRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Meet.objects.all()
    lookup_url_kwarg = "meet_id"
    serializer_class = MeetDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly]

    def patch(self, request, *args, **kwargs):
        meet = self.get_object()

        if meet.user != request.user:
            raise PermissionDenied("모임을 수정할 권한이 없습니다.")

        serializer = self.get_serializer(meet, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "모임 수정이 완료 되었습니다", "id": meet.id}, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.delete()


# /api/meets/aply/{meet_id} [POST]
class MeetApplyView(APIView):
    permission_classes = [IsAuthenticated]

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
        meet.current_people = F('current_people') + 1
        meet.save()
        meet.refresh_from_db()
        return Response(
            {"detail": "모임 지원이 완료되었습니다."}, status=status.HTTP_201_CREATED
        )

# /api/meets/users/{user_id} [GET]
class MeetUserListView(generics.ListAPIView):
    serializer_class = MeetSerializer
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="특정 유저의 모임 목록 조회",
        manual_parameters=[
            openapi.Parameter("title", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("area", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("interest", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("digital_level", openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        queryset = Meet.objects.filter(user_id=user_id)

        title = self.request.query_params.get("title")
        area = self.request.query_params.get("area")
        interest = self.request.query_params.get("interest")
        digital_level = self.request.query_params.get("digital_level")

        if title:
            queryset = queryset.filter(title__icontains=title)
        if area:
            queryset = queryset.filter(area=area)
        if interest:
            queryset = queryset.filter(interest=interest)
        if digital_level:
            queryset = queryset.filter(digitalLevel=digital_level)

        return queryset