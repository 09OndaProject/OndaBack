# cleanup_db_orphaned_files.py

import os
from django.conf import settings
from django.core.management.base import BaseCommand
import boto3

from apps.upload.models import File


class Command(BaseCommand):
    help = "S3에 존재하지 않는 파일을 DB에서 정리 (list_objects_v2 사용)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--prefix",
            type=str,
            help="검사할 S3 Prefix (예: post, profile, meet, certificate, other)",
            choices=["profile", "post", "meet", "certificate", "other"]
        )

    def handle(self, *args, **options):
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME

        prefix_option = options.get("prefix")

        if prefix_option:
            prefix = f"{prefix_option}/"
            self.stdout.write(f"[{prefix_option}] 경로만 검사합니다.")
        else:
            prefix = ""  # 전체 검사
            self.stdout.write("S3 전체 경로를 검사합니다.")

        s3_keys = set()
        continuation_token = None

        while True:
            if continuation_token:
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=prefix,
                    ContinuationToken=continuation_token
                )
            else:
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=prefix
                )

            contents = response.get('Contents', [])
            for obj in contents:
                s3_keys.add(obj['Key'])

            if response.get('IsTruncated'):
                continuation_token = response.get('NextContinuationToken')
            else:
                break

        self.stdout.write(f"S3에서 {len(s3_keys)}개 파일 로딩 완료")

        # DB에서 is_deleted=True 조회
        orphaned_files = File.objects.filter(is_deleted=True)

        if prefix_option:
            orphaned_files = orphaned_files.filter(file__startswith=prefix)

        total_checked = 0
        total_deleted = 0

        for file in orphaned_files:
            total_checked += 1
            s3_key = file.file.name  # 실제 S3 Key

            if s3_key not in s3_keys:
                self.stdout.write(f"파일 없음. DB 삭제: {s3_key}")
                file.delete(soft=False)
                total_deleted += 1

        self.stdout.write(self.style.SUCCESS(f"총 {total_checked}개 중 {total_deleted}개 DB 삭제 완료"))


# 명령어
# python3 manage.py cleanup_db_orphaned_files
# python3 manage.py cleanup_db_orphaned_files --prefix profile

# 명령어 등록
# 아래 경로에 파일이 존재하면 파일명을 기준으로 자동 등록
# <app>/management/commands/*.py


# import os
# from django.conf import settings
# from django.core.management.base import BaseCommand
# from apps.upload.models import File
#
# class Command(BaseCommand):
#     help = "파일이 물리적으로 없는 경우 DB 레코드도 삭제"
#
#     def handle(self, *args, **kwargs):
#         # 파일 경로가 실제로 존재하는지 확인
#         orphaned_files = File.objects.filter(is_deleted=True)
#
#         total_checked = 0
#         total_deleted = 0
#
#         for file in orphaned_files:
#             total_checked += 1
#
#             if file.file:
#                 file_path = os.path.join(settings.MEDIA_ROOT, file.file.name)
#
#                 if not os.path.exists(file_path):  # 실제 파일 존재 여부 확인
#                     # 파일이 실제로 없으면 DB에서 삭제
#                     self.stdout.write(f"파일 없음. DB 삭제: {file.file.name}")
#                     file.delete(soft=False)
#                     total_deleted += 1
#
#         self.stdout.write(self.style.SUCCESS(f"총 {total_checked}개 중 {total_deleted}개 DB 삭제 완료"))
