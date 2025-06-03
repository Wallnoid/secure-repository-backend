
from django.urls import path

from shared_files.views import SharedFileByFileKey, SharedFileView


urlpatterns = [
    path('', SharedFileView.as_view(), name='shared_files'),
    path('by-file-key', SharedFileByFileKey.as_view(), name='shared_files_by_file_key'),
]



