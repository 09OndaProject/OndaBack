from django.urls import path

from . import views

urlpatterns = [
    #게시글 CRUD
    path("", views.PostListCreateView.as_view()),  # GET/POST
    path("<int:pk>/", views.PostDetailView.as_view()),  # GET/PATCH/DELETE

    #댓글/대댓글 CRUD
    path("<int:post_id>/comments/", views.CommentListCreateView.as_view()),    # GET/POST
    path("<int:post_id>/comments/<int:pk>/", views.CommentDetailView.as_view()),  # GET/PATCH/DELETE

    #좋아요
    path("<int:post_id>/like/", views.LikeToggleView.as_view()),  # POST
]
