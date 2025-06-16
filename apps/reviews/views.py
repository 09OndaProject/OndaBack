from datetime import timedelta

from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.meet.models import Meet, MeetApply

from .models import Review
from .permissions import IsOwnerOrReadOnlyWithin7Days
from .serializers import ReviewCreateSerializer, ReviewDisplaySerializer


# 페이지네이션 설정
class ReviewPagination(PageNumberPagination):
    page_size = 6


# 후기 요약 (상위 4개 + 평균 평점 + 총 개수)
class ReviewSummaryView(generics.GenericAPIView):
    serializer_class = ReviewDisplaySerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="후기 요약 조회",
        tags=["리뷰 API"],
        manual_parameters=[
            openapi.Parameter(
                "meet_id",
                openapi.IN_PATH,
                description="모임 ID",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response("리뷰 요약 정보", ReviewDisplaySerializer(many=True))
        },
    )
    def get(self, request, meet_id):
        meet = get_object_or_404(Meet, id=meet_id, is_deleted=False)

        # 삭제된 모임이어도 리뷰는 통계 집계 (요약에 포함)
        top_reviews = (
            Review.objects.filter(meet=meet)
            .select_related("user")
            .order_by("-rating", "-created_at")[:4]
        )
        summary = Review.objects.filter(meet=meet).aggregate(
            avg=Avg("rating"), count=Count("id")
        )

        serializer = self.get_serializer(top_reviews, many=True)
        return Response(
            {
                "average_rating": round(summary["avg"] or 0, 2),
                "review_count": summary["count"],
                "top_reviews": serializer.data,
            }
        )


# 후기 목록 + 작성
class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewDisplaySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = ReviewPagination

    def get_queryset(self):
        # 삭제된 모임 제외
        return (
            Review.objects.select_related("user", "meet")
            .filter(meet_id=self.kwargs["meet_id"], meet__is_deleted=False)
            .order_by("-created_at")
        )

    @swagger_auto_schema(
        operation_summary="리뷰 목록 조회",
        tags=["리뷰 API"],
        manual_parameters=[
            openapi.Parameter(
                "meet_id",
                openapi.IN_PATH,
                description="모임 ID",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={200: ReviewDisplaySerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        summary = queryset.aggregate(avg=Avg("rating"))

        serializer = self.get_serializer(page or queryset, many=True)
        return (
            self.get_paginated_response(
                {
                    "average_rating": round(summary["avg"] or 0, 2),
                    "reviews": serializer.data,
                }
            )
            if page
            else Response(
                {
                    "average_rating": round(summary["avg"] or 0, 2),
                    "reviews": serializer.data,
                }
            )
        )

    @swagger_auto_schema(
        operation_summary="리뷰 작성",
        tags=["리뷰 API"],
        request_body=ReviewCreateSerializer,
        responses={201: ReviewDisplaySerializer()},
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        meet_id = self.kwargs["meet_id"]
        meet = get_object_or_404(Meet, id=meet_id, is_deleted=False)

        if not MeetApply.objects.filter(user=user, meet=meet).exists():
            raise ValidationError("이 모임에 참가하지 않았습니다.")

        if Review.objects.filter(user=user, meet=meet).exists():
            raise ValidationError("이미 리뷰를 작성하셨습니다.")

        today = timezone.now().date()
        if today < meet.date:
            raise ValidationError("모임이 종료된 후에만 리뷰를 작성할 수 있습니다.")
        if today > meet.date + timedelta(days=14):
            raise ValidationError("모임 종료 후 14일이 지나 리뷰 작성이 불가능합니다.")

        serializer = ReviewCreateSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        review = serializer.save(user=user, meet=meet)

        response_serializer = ReviewDisplaySerializer(review)
        return Response(
            {
                "message": "리뷰가 성공적으로 작성되었습니다.",
                "data": response_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


# 후기 상세 (조회 / 수정 / 삭제)
class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.select_related("user", "meet").all()
    serializer_class = ReviewDisplaySerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnlyWithin7Days,
    ]

    @swagger_auto_schema(operation_summary="리뷰 상세 조회", tags=["리뷰 API"])
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="리뷰 수정",
        tags=["리뷰 API"],
        request_body=ReviewCreateSerializer,
    )
    def patch(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        updated_instance = self.get_object()
        response_serializer = self.get_serializer(updated_instance)
        return Response(
            {
                "message": "리뷰가 성공적으로 수정되었습니다.",
                "data": response_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_summary="리뷰 삭제",
        tags=["리뷰 API"],
        responses={204: openapi.Response("삭제 성공")},
    )
    def delete(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            {"message": "리뷰가 성공적으로 삭제되었습니다."},
            status=status.HTTP_204_NO_CONTENT,
        )

    @swagger_auto_schema(auto_schema=None)
    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT")


# 내가 작성한 후기 목록
class MyReviewListView(generics.ListAPIView):
    serializer_class = ReviewDisplaySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ReviewPagination

    def get_queryset(self):
        return (
            Review.objects.select_related("user", "meet")
            .filter(user=self.request.user)
            .order_by("-created_at")
        )

    @swagger_auto_schema(
        operation_summary="내가 작성한 리뷰 목록 조회",
        tags=["리뷰 API"],
        responses={200: ReviewDisplaySerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
