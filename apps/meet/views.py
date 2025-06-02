# meet/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Meet, MeetApply
from .serializers import MeetSerializer, MeetDetailSerializer
#from .permissions import IsOwnerOrReadOnly


# /api/meets [GET, POST]
class MeetListCreateView(generics.ListCreateAPIView):
    queryset = Meet.objects.all().order_by('-created_at')
    serializer_class = MeetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# /api/meets/{meet_id} [GET, PATCH, DELETE]
class MeetRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Meet.objects.all()
    lookup_url_kwarg = 'meet_id'
    serializer_class = MeetDetailSerializer
    #permission_classes = [IsOwnerOrReadOnly]

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()


# /api/meets/aply/{meet_id} [POST]
class MeetApplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, meet_id):
        meet = get_object_or_404(Meet, pk=meet_id)

        if MeetApply.objects.filter(user=request.user, meet=meet).exists():
            return Response({'detail': '이미 지원한 모임입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        if meet.status != '모집중':
            return Response({'detail': '모집이 종료된 모임입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        MeetApply.objects.create(user=request.user, meet=meet)
        meet.current_people += 1
        meet.save()

        return Response({'detail': '모임 지원이 완료되었습니다.'}, status=status.HTTP_201_CREATED)
