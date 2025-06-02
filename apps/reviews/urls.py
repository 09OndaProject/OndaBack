from django.urls import path

from .views import (
    ReviewDetailView,
    ReviewListCreateView,
    ReviewSummaryView,
)

urlpatterns = [
    path('meetings/<int:meet_id>/reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('meetings/<int:meet_id>/reviews/summary/', ReviewSummaryView.as_view(), name='review-summary'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
]