from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver

from apps.leaders.models import LeaderApplication, LeaderCertificate
from apps.meet.models import Meet
from apps.posts.models import Post, PostImage

User = get_user_model()


@receiver(post_delete, sender=User)
@receiver(pre_delete, sender=Post)
@receiver(pre_delete, sender=LeaderApplication)
@receiver(post_delete, sender=Meet)
def auto_delete_file_if_unused(sender, instance, **kwargs):

    if sender == User or sender == Meet:
        file = instance.file
    elif sender == Post and instance.post_image:
        file = instance.post_image.file
    elif sender == LeaderApplication and instance.leader_certificate:
        file = instance.leader_certificate.file

    is_used_elsewhere = any(
        [
            User.objects.filter(file=file).exists(),
            PostImage.objects.filter(file=file).exists(),
            LeaderCertificate.objects.filter(file=file).exists(),
            Meet.objects.filter(file=file).exists(),
        ]
    )

    if not is_used_elsewhere:
        # file.file.delete(save=False)  # 실제 파일 삭제
        file.delete()  # File 모델 소프트 딜리트 후 모아서 처리


# 모델의 삭제 동작 시그널 발생
# 비동기 처리 혹은 소프트 딜리트 후 일괄 삭제 처리

# 시그널
# 모델의 save() 동작이나 delete() 등의 동작이 일어날 때 감지.
# 한번에 여러 쿼리를 실행하는 bulk 동작에선 감지 안됨. (모델의 save(), delete() 등의 메서드 사용안함.)
# cascade 동작은 데이터 베이스 내에서 일어나기 때문에 감지 안됨.

# 쿼리 이벤트 종류
# pre_init  - 인스턴스 생성 전 (MyModel(**kwargs) 로 인스턴스 생성 직전)-> 생성자 실행 전, 초기화 인자 확인 가능
# post_init - 인스턴스 생성 후 (DB에서 로드되거나 수동 생성되었을 때)
# pre_save - 저장 전 (instance.save() 실행 전) → 유효성 검사, 자동 필드 처리에 유용
# post_save - 저장 후 (instance.save() 실행 후) → 로그 기록, 외부 API 호출 등 후처리에 사용
# pre_delete - 삭제 전 (instance.delete() 전) -> 삭제 직전 후속 작업 처리용
# post_delete - 삭제 후 (instance.delete() 후) -> 삭제된 후 파일 삭제, 정리 작업 등
# m2m_changed - ManyToManyField 변경될 때 (add, remove, clear 등 발생 시점에 호출) -> 관계 변경 추적 가능

# any() = or
