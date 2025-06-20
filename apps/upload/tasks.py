# from celery import shared_task
# from django.utils.timezone import now
# from datetime import timedelta
#
# from apps.upload.models import File
#
#
# @shared_task
# def cleanup_orphaned_files_task():
#     threshold = now() - timedelta(days=7)
#     files_to_delete = File.objects.filter(is_deleted=True, deleted_at__lt=threshold)
#
#     count = 0
#     for file in files_to_delete:
#         try:
#             file.delete(soft=False)
#             count += 1
#         except Exception as e:
#             # 로깅만 처리 (예: Sentry)
#             print(f"Error deleting file: {file.file.name} -> {e}")
#
#     return f"{count} orphaned files deleted"
