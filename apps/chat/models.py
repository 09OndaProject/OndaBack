from django.conf import settings
from django.db import models

from utils.models import TimestampModel


# 하나의 모임(Meet)은 하나의 채팅방만 가질 수 있음
class GroupChatRoom(TimestampModel):
    meet = models.OneToOneField("meet.Meet", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.meet.title}의 채팅방"


# 채팅방에 참여 중인 유저를 저장
class GroupChatMembership(TimestampModel):
    room = models.ForeignKey(
        GroupChatRoom, on_delete=models.CASCADE, related_name="members"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("room", "user")  # 같은 유저가 중복 입장 못하도록 제한

    def __str__(self):
        return f"{self.user} in {self.room}"


# 실제로 주고받는 메시지를 저장
class GroupChatMessage(TimestampModel):
    room = models.ForeignKey(
        GroupChatRoom, on_delete=models.CASCADE, related_name="messages"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return f"[{self.timestamp}] {self.user.username}: {self.content}"
