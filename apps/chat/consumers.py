import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import GroupChatRoom, GroupChatMessage

class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # URL에서 room_id를 받아 채팅방 식별
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # 그룹에 참가 (channels 내부 그룹)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept() # 클라이언트 연결 수락

    async def disconnect(self, close_code):
        # 그룹에서 퇴장
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data['content']
        user_id = self.scope['user'].id

        # DB에 메시지 저장 (동시 함수 -> 비동기로 감싸기)
        await self.save_message(self.room_id, user_id, content)

        # 같은 그룹 모든 유저에게 메시지 전송
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'content': content,
                'user_id': user_id,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'user_id': event['user_id'],
            'content': event['content'],
        }))

    @database_sync_to_async
    def save_message(self, room_id, user_id, content):
        return GroupChatMessage.objects.create(
            room = room_id,
            user_id = user_id,
            content = content
        )