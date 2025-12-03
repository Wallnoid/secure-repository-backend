from django.urls import path
from . import views

urlpatterns = [
    path('file/', views.FileAuditView.as_view(), name='file-audit'),
    path('all-files/', views.AllFilesAuditView.as_view(), name='all-files-audit'),
    path('logs/files/', views.FileLogsView.as_view(), name='file-logs'),
    path('logs/folders/', views.FolderLogsView.as_view(), name='folder-logs'),
    path('reports/files/', views.FileReportView.as_view(), name='file-report'),
    path('reports/folders/', views.FolderReportView.as_view(), name='folder-report'),
    path('reports/folder-files/', views.FolderFilesAuditView.as_view(), name='folder-files-audit'),
] 