from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.user.views.admin_views import AdminUserViewSet

router = DefaultRouter(trailing_slash=False)

router.register(r"admin/users", AdminUserViewSet, basename="admin-users")

urlpatterns = [
    path("", include(router.urls)),
]
