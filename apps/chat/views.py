from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from apps.chat.models import GroupChatRoom, GroupChatMembership
from apps.meet.models import Meet, MeetApply


class JoinGroupChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, meet_id):
        # 1. 해당 모임 가져오기 (존재하지 않으면 404)
        meet = get_object_or_404(Meet, id=meet_id)

        # 2. 현재 유저가 모임 참여자인지 확인
        is_participant = MeetApply.objects.filter(meet=meet, user=request.user).exists()
        if not is_participant and meet.user != request.user:
            return Response(
                {"detail": "모임에 참여하지 않은 유저입니다."},
                status=status.HTTP_403_FORBIDDEN
            )

        # 3. 채팅방이 없으면 생성
        room, created = GroupChatRoom.objects.get_or_create(meet=meet)

        # 4. 채팅방에 참여자로 추가 (중복 방지)
        GroupChatMembership.objects.get_or_create(room=room, user=request.user)

        return Response(
            {"room_id": room.id, "message": "채팅방에 입장했습니다."},
            status=status.HTTP_200_OK
        )