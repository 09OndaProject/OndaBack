from django.urls import path

from . import views

urlpatterns = [
    path("posts", views.PostListCreateView.as_view()),  # GET/POST
    path("posts/<int:pk>", views.PostDetailView.as_view()),  # GET/PATCH/DELETE
]
