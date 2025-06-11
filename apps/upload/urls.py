from django.urls import path

from .views import FileDeleteView, FileListView, FileUploadView

prefix = "files"

urlpatterns = [
    path(prefix + "/list", FileListView.as_view(), name="list"),
    path(prefix + "/upload", FileUploadView.as_view(), name="upload"),
    path(prefix + "/delete", FileDeleteView.as_view(), name="delete"),
    # path(prefix+"/page", file_manager_view, name="file-manager-page"),
]
