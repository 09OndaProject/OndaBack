# cleanup_orphaned_files.py

import os
from datetime import timedelta

import boto3
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import now

from apps.upload.models import File


class Command(BaseCommand):
    help = "Soft-deleted 파일 중 일정 기간 지난 것을 실제 삭제 (DB + 저장소)"

    def handle(self, *args, **kwargs):
        # 삭제 기준: soft delete 후 7일 지난 파일들
        threshold = now() - timedelta(days=7)

        # 7일 전보다 삭제일이 작은 것들 (7일이 지난 파일들) (7일이 지나지 않으면 삭제일이 더 큼)
        files_to_delete = File.objects.filter(is_deleted=True, deleted_at__lt=threshold)

        total = files_to_delete.count()
        if total == 0:
            self.stdout.write("삭제할 파일이 없습니다.")
            return

        if settings.DJANGO_ENV == "prod":
            self.stdout.write("배포 환경 실행")
            # S3 클라이언트 초기화
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )

            # S3 버킷 이름
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME

            # 삭제할 파일 키 목록
            delete_objects = []

            # 파일과 썸네일의 S3 키 수집
            for file in files_to_delete:
                if file.file:
                    file_key = file.file.name
                    delete_objects.append({"Key": file_key})

                if file.thumbnail:
                    thumbnail_key = file.thumbnail.name
                    delete_objects.append({"Key": thumbnail_key})

            # S3에서 일괄 삭제 (최대 1000개까지 한 번에 삭제 가능)
            if delete_objects:
                # 1000개씩 나누어서 처리
                for i in range(0, len(delete_objects), 1000):
                    try:
                        s3_client.delete_objects(
                            Bucket=bucket_name,
                            Delete={"Objects": delete_objects[i : i + 1000]},
                        )
                    except Exception as e:
                        self.stderr.write(f"S3 삭제 중 오류 발생")

            # 데이터베이스에서 한 번에 삭제
            files_to_delete.delete()
        else:
            self.stdout.write("로컬 환경 실행")
            for file in files_to_delete:
                file_path = file.file.name
                try:
                    self.stdout.write(f"삭제 중: {file_path}")
                    file.delete(soft=False)  # 실제 파일 + DB 삭제
                except Exception as e:
                    self.stderr.write(f"삭제 실패: {file_path} -> {e}")

        self.stdout.write(self.style.SUCCESS(f"총 {total}개 파일 정리 완료"))


# 명령어
# python3 manage.py cleanup_orphaned_files

# 명령어 등록
# 아래 경로에 파일이 존재하면 파일명을 기준으로 자동 등록
# <app>/management/commands/*.py
