from datetime import timedelta

from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrReadOnlyWithin7Days(BasePermission):
    """
    작성자 본인만 리뷰 수정/삭제 가능하며,
    작성 후 7일 이내에만 가능하도록 제한
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if obj.user != request.user:
            raise PermissionDenied("본인만 리뷰를 수정하거나 삭제할 수 있습니다.")

        if timezone.now() > obj.created_at + timedelta(days=7):
            raise PermissionDenied("리뷰 작성 후 7일이 지나 수정/삭제할 수 없습니다.")

        return True
