from django.urls import path
from audit.views import FileAuditView, AllFilesAuditView

urlpatterns = [
    path('file/', FileAuditView.as_view(), name='file-audit'),
    path('all-files/', AllFilesAuditView.as_view(), name='all-files-audit'),
] 