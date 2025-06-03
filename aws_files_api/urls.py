
from django.urls import path

from .views import CreateBucket, FilesView, PrincipalFolder, DownloadFile, FolderCrud

urlfilepatterns = [
    path('', FilesView.as_view(), name='get_docs'),
    path('download-file/', DownloadFile.as_view(), name='download_file'),
    path('create-bucket/', CreateBucket.as_view(), name='create_bucket'),
  
]


urlFolderpatterns = [
    path('', FolderCrud.as_view(), name='folder_crud'),
    path('principal-folders/', PrincipalFolder.as_view(), name='principal_folder'),
]



