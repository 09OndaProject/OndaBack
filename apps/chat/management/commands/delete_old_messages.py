# apps/chat/management/commands/delete_old_messages.py

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.chat.models import GroupChatMessage
from apps.user.models import User


class Command(BaseCommand):
    help = "탈퇴한지 7일 이상 지난 유저의 채팅 메시지를 삭제합니다."

    def handle(self, *args, **options):
        # 7일 전 시간 계산
        cutoff_date = timezone.now() - timedelta(days=7)

        # 7일 이상 지난 탈퇴 유저 조회
        users_to_cleanup = User.objects.filter(
            is_deleted=True, deleted_at__lte=cutoff_date
        )

        # 삭제 진행
        for user in users_to_cleanup:
            deleted_count, _ = GroupChatMessage.objects.filter(user=user).delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f"[삭제 완료] {user.email} - 삭제된 메시지 수: {deleted_count}"
                )
            )

        if not users_to_cleanup.exists():
            self.stdout.write(self.style.WARNING("삭제 대상 유저가 없습니다."))
