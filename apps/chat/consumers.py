import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

from .models import GroupChatMembership, GroupChatMessage, GroupChatRoom

User = get_user_model()


class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 현재 접속한 유저 정보
        self.user = self.scope["user"]

        # 인증되지 않은 사용자일 경우 연결 거부
        if not self.user.is_authenticated:
            await self.close()
            return

        # URL에서 room_id 추출 -> 그룹 이름 지정
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        # 이 유저가 해당 방의 멤버인지 DB에서 확인
        is_member = await database_sync_to_async(
            GroupChatMembership.objects.filter(
                room_id=self.room_id, user=self.user
            ).exists
        )()

        if not is_member:
            await self.close()  # 참여자가 아니면 연결 종료
            return

        # 채널 그룹에 참여
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        # 연결 수락
        await self.accept()

    async def disconnect(self, close_code):
        """
        연결 종료 시 호출되는 메서드
        그룹에서 안전하게 퇴장 처리
        """
        # self.room_group_name이 정의되어 있으면 제거
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name,
            )

    async def receive(self, text_data):
        """
        클라이언트로부터 메시지를 수신했을 때 호출됨
        """
        data = json.loads(text_data)
        content = data.get("message", "")
        user = self.scope["user"]

        # 인증되지 않은 사용자 메시지 차단
        if not user.is_authenticated:
            await self.close()
            return

        # 메시지를 DB에 저장
        await self.save_message(self.room_id, user, content)

        # 그룹 내 모든 유저에게 메시지 전송
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "user_id": user.id,
                "nickname": user.nickname,
                "message": content,
            },
        )

    async def chat_message(self, event):
        """
        그룹 메시지를 받아 클라이언트에 전송
        """
        await self.send(
            text_data=json.dumps(
                {
                    "user_id": event["user_id"],
                    "nickname": event["nickname"],
                    "message": event["message"],
                }
            )
        )

    @database_sync_to_async
    def save_message(self, room_id, user, content):
        # 데이터베이스에 메시지 저장 (동기 -> 비동기 변환)
        try:
            room = GroupChatRoom.objects.get(id=room_id)
        except GroupChatRoom.DoesNotExist:
            raise ValueError("채팅방이 존재하지 않습니다.")

        # user가 AnonymousUser가 아니면 그대로 사용
        if user.is_authenticated:
            return GroupChatMessage.objects.create(
                room=room,
                user=user,
                content=content,
            )
        else:
            raise ValueError("인증되지 않은 사용자입니다.")
