from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete
from django.dispatch import receiver

from apps.leaders.models import LeaderCertificate
from apps.posts.models import PostImage

User = get_user_model()


@receiver(post_delete, sender=User)
@receiver(post_delete, sender=PostImage)
@receiver(post_delete, sender=LeaderCertificate)
def auto_delete_file_if_unused(sender, instance, **kwargs):
    file = instance.file
    is_used_elsewhere = (
        User.objects.filter(file=file).exists()
        or PostImage.objects.filter(file=file).exists()
        or LeaderCertificate.objects.filter(file=file).exists()
    )

    if not is_used_elsewhere:
        # file.file.delete(save=False)  # 실제 파일 삭제
        file.delete()  # File 모델 삭제
