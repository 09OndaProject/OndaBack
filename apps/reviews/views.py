from django.db.models import Avg
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from utils.responses.reviews import (
    REVIEW_ALREADY_WRITTEN,
    REVIEW_CREATE_SUCCESS,
    REVIEW_DELETE_SUCCESS,
    REVIEW_UPDATE_SUCCESS,
)

from .models import Review
from .permissions import IsOwnerOrReadOnlyWithin7Days
from .serializers import ReviewCreateSerializer, ReviewDisplaySerializer


# ✅ 페이지네이션 설정
class ReviewPagination(PageNumberPagination):
    page_size = 6


# ✅ 후기 요약 (상위 4개 + 평균 평점 + 총 개수)
class ReviewSummaryView(generics.GenericAPIView):
    serializer_class = ReviewDisplaySerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="모임 후기 요약 조회 (상위 4개 + 평균 평점)",
        tags=["리뷰 API"],
        manual_parameters=[
            openapi.Parameter(
                "meet_id",
                openapi.IN_PATH,
                description="모임 ID",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        responses={
            200: openapi.Response(
                "리뷰 요약 정보 반환", ReviewDisplaySerializer(many=True)
            )
        },
    )
    def get(self, request, meet_id):
        reviews = Review.objects.filter(meet_id=meet_id).order_by("-created_at")[:4]
        avg_rating = (
            Review.objects.filter(meet_id=meet_id).aggregate(avg=Avg("rating"))["avg"]
            or 0
        )
        serializer = self.get_serializer(reviews, many=True)
        return Response(
            {
                "average_rating": round(avg_rating, 2),
                "review_count": Review.objects.filter(meet_id=meet_id).count(),
                "top_reviews": serializer.data,
            }
        )


# ✅ 후기 목록 + 작성
class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewDisplaySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = ReviewPagination

    def get_queryset(self):
        meet_id = self.kwargs["meet_id"]
        return Review.objects.filter(meet_id=meet_id).order_by("-created_at")

    @swagger_auto_schema(
        operation_summary="특정 모임의 리뷰 전체 목록 조회",
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
            200: openapi.Response(
                "리뷰 목록 및 평균 평점 반환", ReviewDisplaySerializer(many=True)
            )
        },
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        avg_rating = queryset.aggregate(avg=Avg("rating"))["avg"] or 0

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(
                {"average_rating": round(avg_rating, 2), "reviews": serializer.data}
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {"average_rating": round(avg_rating, 2), "reviews": serializer.data}
        )

    @swagger_auto_schema(
        operation_summary="리뷰 작성",
        tags=["리뷰 API"],
        request_body=ReviewCreateSerializer,
        responses={201: openapi.Response("작성 성공", ReviewDisplaySerializer())},
    )
    def create(self, request, *args, **kwargs):
        user = request.user
        meet_id = self.kwargs["meet_id"]

        if Review.objects.filter(user=user, meet_id=meet_id).exists():
            raise ValidationError(REVIEW_ALREADY_WRITTEN)

        serializer = ReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user, meet_id=meet_id)

        response_serializer = ReviewDisplaySerializer(serializer.instance)
        return Response(
            {
                "message": REVIEW_CREATE_SUCCESS["message"],
                "code": REVIEW_CREATE_SUCCESS["code"],
                "data": response_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


# ✅ 후기 상세 조회 / 수정 / 삭제
class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewDisplaySerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnlyWithin7Days,
    ]

    @swagger_auto_schema(
        operation_summary="리뷰 상세 조회",
        tags=["리뷰 API"],
        responses={200: ReviewDisplaySerializer()},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="리뷰 수정",
        tags=["리뷰 API"],
        request_body=ReviewCreateSerializer,
        responses={200: ReviewDisplaySerializer()},
    )
    def patch(self, request, *args, **kwargs):
        response = self.partial_update(request, *args, **kwargs)
        return Response(
            {
                "message": REVIEW_UPDATE_SUCCESS["message"],
                "code": REVIEW_UPDATE_SUCCESS["code"],
                "data": response.data,
            },
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_summary="리뷰 삭제",
        tags=["리뷰 API"],
        responses={204: openapi.Response("삭제 성공")},
    )
    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        return Response(
            {
                "message": REVIEW_DELETE_SUCCESS["message"],
                "code": REVIEW_DELETE_SUCCESS["code"],
            },
            status=status.HTTP_204_NO_CONTENT,
        )

    # PUT 비허용
    @swagger_auto_schema(auto_schema=None)
    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT")
