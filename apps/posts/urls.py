from django.urls import path

from . import views

urlpatterns = [
    path("", views.PostListCreateView.as_view()),  # GET/POST
    path("<int:pk>/", views.PostDetailView.as_view()),  # GET/PATCH/DELETE
]
