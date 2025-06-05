from django.urls import path

from .views import FileListUploadView, FileUpdateDeleteView

prefix = "files"

urlpatterns = [
    path(prefix + "", FileListUploadView.as_view(), name="file-upload"),
    path(prefix + "/<int:pk>", FileUpdateDeleteView.as_view(), name="file-detail"),
    # path(prefix+"/page", file_manager_view, name="file-manager-page"),
]
