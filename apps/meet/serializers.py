from datetime import timedelta

from django.db.models import Avg
from django.utils import timezone
from rest_framework import serializers

from apps.options.serializers.area import AreaSerializer
from apps.options.serializers.category import CategorySerializer
from apps.options.serializers.digital_level import DigitalLevelSerializer
from apps.options.serializers.interest import InterestSerializer
from apps.upload.serializers import FileSerializer
from apps.user.models import User

from .models import Meet


class MeetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meet
        fields = [
            "title",
            "description",
            "area",
            "digital_level",
            "category",
            "date",
            "start_time",
            "end_time",
            "location",
            "contact",
            "session_count",
            "max_people",
            "file",
            "application_deadline",
            "link",
        ]

        extra_kwargs = {
            "link": {"required": False},
            "file": {"required":False}
        }  # 일단 오픈채팅방 링크는 null가능으로

    def validate(self, data):
        now = timezone.now()

        # application_deadline 유효성 검사
        application_deadline = data.get("application_deadline")
        if application_deadline and application_deadline < now:
            raise serializers.ValidationError(
                {"application_deadline": "마감일은 현재 시각보다 이후여야 합니다."}
            )

        # date 유효성 검사
        date = data.get("date")
        if date and date < now.date():
            raise serializers.ValidationError(
                {"date": "모임 날짜는 오늘 이후여야 합니다."}
            )

        return data


class MeetListSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField()
    area = serializers.CharField(source="area.full_path", read_only=True)
    leader_nickname = serializers.CharField(source="user.nickname", read_only=True)
    leader_image = serializers.SerializerMethodField()

    def get_leader_image(self, obj):
        if obj.user.file:
            return FileSerializer(obj.user.file).data
        return None

    class Meta:
        model = Meet
        fields = [
            "id",
            "title",
            "description",
            "area",
            "date",
            "max_people",
            "current_people",
            "application_deadline",
            "status",
            "session_count",
            "leader_nickname",
            "leader_image",
        ]


class MeetUserListSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField()
    area = serializers.CharField(source="area.full_path", read_only=True)

    class Meta:
        model = Meet
        fields = [
            "id",
            "title",
            "description",
            "area",
            "date",
            "max_people",
            "current_people",
            "application_deadline",
            "status",
            "session_count",
        ]


class LeaderSerializer(serializers.ModelSerializer):
    file = FileSerializer(read_only=True)
    interest = InterestSerializer(read_only=True)
    bio = serializers.SerializerMethodField(read_only=True)

    def get_bio(self, obj):
        leader_app = getattr(obj, "leader_application", None)
        if leader_app:
            return leader_app.bio
        return None

    class Meta:
        model = User
        fields = [
            "id",
            "nickname",
            "interest",
            "bio",
            "file",
        ]


class MeetUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meet
        fields = [
            "title",
            "description",
            "area",
            "digital_level",
            "category",
            "date",
            "start_time",
            "end_time",
            "location",
            "contact",
            "session_count",
            "max_people",
            "application_deadline",
            "link",
            "file",
        ]

    def validate(self, data):
        from django.utils import timezone

        now = timezone.now()

        application_deadline = data.get("application_deadline")
        if application_deadline and application_deadline < now:
            raise serializers.ValidationError(
                {"application_deadline": "마감일은 현재 시각보다 이후여야 합니다."}
            )

        date = data.get("date")
        if date and date < now.date():
            raise serializers.ValidationError(
                {"date": "모임 날짜는 오늘 이후여야 합니다."}
            )

        return data


class MeetDetailSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField()
    file = FileSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    digital_level = DigitalLevelSerializer(read_only=True)
    leader = LeaderSerializer(source="user", read_only=True)
    # meet를 fk로 하는 meetapply의 유저 명단
    member = serializers.SerializerMethodField()
    # 리뷰의 평점 평균
    meet_rating = serializers.SerializerMethodField()
    # 리뷰 개수
    review_count = serializers.SerializerMethodField()
    # 일정 계산(date을 시작일로 매주 총 session_count번의 일정의 날짜를 계산)
    schedule = serializers.SerializerMethodField()
    # 진행방법 태그명으로 반환
    contact = serializers.SerializerMethodField()

    def get_member(self, obj):
        return [
            {
                "id": app.user.id,
                "nickname": app.user.nickname,
                "file": FileSerializer(app.user.file).data if app.user.file else None,
            }
            for app in obj.applications.all()
        ]

    def get_meet_rating(self, obj):
        return obj.reviews.aggregate(avg=Avg("rating"))["avg"] or 0

    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_schedule(self, obj):
        if not obj.date or not obj.session_count:
            return []
        return [
            (obj.date + timedelta(weeks=i)).isoformat()
            for i in range(obj.session_count)
        ]

    def get_contact(self, obj):
        return obj.get_contact_display()

    class Meta:
        model = Meet
        fields = [
            "id",
            "title",
            "description",
            "digital_level",
            "category",
            "session_count",
            "location",
            "contact",
            "max_people",
            "current_people",
            "file",
            "status",
            "application_deadline",
            "member",
            "leader",
            "meet_rating",
            "review_count",
            "schedule",
            "link",
        ]
