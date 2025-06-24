from django.urls import path

from .views import (
    LeaderReviewListView,
    MyReviewListView,
    ReviewDetailView,
    ReviewListCreateView,
    ReviewSummaryView,
)

urlpatterns = [
    path(
        "meets/<int:meet_id>/reviews",
        ReviewListCreateView.as_view(),
        name="review-list-create",
    ),
    path(
        "meets/<int:meet_id>/reviews/summary",
        ReviewSummaryView.as_view(),
        name="review-summary",
    ),
    path("reviews/<int:pk>", ReviewDetailView.as_view(), name="review-detail"),
    path("users/reviews", MyReviewListView.as_view(), name="my-review-list"),
    path("reviews/my-meet", LeaderReviewListView.as_view(), name="leader-review-list"),
]
