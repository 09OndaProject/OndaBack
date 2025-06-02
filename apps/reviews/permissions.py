from rest_framework.permissions import BasePermission, SAFE_METHODS
from datetime import timedelta
from django.utils import timezone

class IsOwnerOrReadOnlyWithin7Days(BasePermission):
    """
    작성자만 수정/삭제 가능 (작성일로부터 7일 이내)
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if obj.user != request.user:
            return False
        return timezone.now() - obj.created_at <= timedelta(days=7)