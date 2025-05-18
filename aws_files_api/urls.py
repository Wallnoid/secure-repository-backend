
from django.urls import path

from .views import CreateBucket, GetFilesView, UploadFile, DownloadFile, FolderCrud

urlpatterns = [
    path('', GetFilesView.as_view(), name='get_docs'),
    path('download-file', DownloadFile.as_view(), name='download_file'),
    path('upload-file', UploadFile.as_view(), name='upload_file'),
    path('create-bucket', CreateBucket.as_view(), name='create_bucket'),
    path('folders', FolderCrud.as_view(), name='folder_crud'),
]



