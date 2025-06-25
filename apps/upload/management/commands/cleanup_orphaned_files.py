import os

import boto3
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.upload.models import File


class Command(BaseCommand):
    help = "DB에 존재하지 않는 S3 파일을 일괄 삭제"

    def handle(self, *args, **options):

        # S3 클라이언트 초기화
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        # S3 버킷 이름
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        prefix = "media/"

        self.stdout.write("DB에 존재하지 않는 S3 파일 정리 시작")

        # DB에 존재하는 파일 목록 (S3 Key)
        valid_keys = set(
            f"{file.file.storage.location}/{file.file.name}"
            for file in File.objects.all()
            if file.file
        )

        # S3에 존재하는 모든 파일 목록
        s3_keys = set()
        continuation_token = None

        while True:
            if continuation_token:
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=prefix,
                    ContinuationToken=continuation_token,
                )
            else:
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=prefix,
                )

            contents = response.get("Contents", [])  # S3 파일 목록
            for obj in contents:
                s3_keys.add(obj["Key"])

            if response.get(
                "IsTruncated"
            ):  # 현재 요청으로 다 못 가져왔는지 여부 (1000개 이상일 시)
                continuation_token = response.get(
                    "NextContinuationToken"
                )  # 다음 페이지를 가져오기 위한 토큰 (S3가 응답으로 주는 페이징 키)
            else:
                break

        self.stdout.write(f"S3 총 파일 수: {len(s3_keys)}")
        self.stdout.write(f"DB에 존재하는 파일 수: {len(valid_keys)}")

        # DB에 없는 S3 파일
        orphaned_keys = list(s3_keys - valid_keys)

        self.stdout.write(f"삭제할 파일 수: {len(orphaned_keys)}")

        if orphaned_keys:
            for i in range(0, len(orphaned_keys), 1000):
                batch = orphaned_keys[i : i + 1000]
                delete_objects = [{"Key": key} for key in batch]

                response = s3_client.delete_objects(
                    Bucket=bucket_name,
                    Delete={"Objects": delete_objects},
                )

                deleted = response.get("Deleted", [])
                self.stdout.write(f"삭제 완료: {len(deleted)}개 (Batch {i//1000 + 1})")

            self.stdout.write(self.style.SUCCESS("DB에 없는 S3 파일 일괄 삭제 완료"))
        else:
            self.stdout.write("삭제할 파일이 없습니다.")




