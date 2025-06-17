from chat.models import GroupChatMembership, GroupChatRoom
from meet.models import MeetApply


#  채팅방이 없는 경우 새로 만들고, 해당 유저를 참여자로 추가하는 로직
def join_or_create_chatroom(user, meet):
    # 채팅방이 없으면 만들고, 이미 있으면 가져옴
    room, created = GroupChatRoom.objects.get_or_create(meet=meet)

    # 해당 유저가 모임에 참여한 상태인지 확인
    is_participant = MeetApply.objects.filter(user=user, meet=meet).exists() or (
        meet.user == user
    )
    if not is_participant:
        raise PermissionError("모임에 참여하지 않은 유저는 채팅에 참여할 수 없습니다.")

    # 채팅방 참여 정보 생성 (중복 방지)
    GroupChatMembership.objects.get_or_create(user=user, room=room)

    return room  # 프론트엔드에 room 정보 리턴
