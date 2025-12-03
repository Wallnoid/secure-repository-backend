from django.contrib import admin
from .models import FileLog, FolderLog


@admin.register(FileLog)
class FileLogAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user_email', 'action', 'file_name', 
        'success', 'timestamp'
    ]
    list_filter = [
        'action', 'success', 'timestamp'
    ]
    search_fields = [
        'user_email', 'user_id', 'file_name', 'file_key',
        'owner_user_email', 'shared_with_user_email'
    ]
    readonly_fields = [
        'id', 'timestamp'
    ]
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Main Information', {
            'fields': ('user_id', 'user_email', 'action', 'timestamp', 'success')
        }),
        ('File Details', {
            'fields': ('file_key', 'file_name', 'file_size', 'old_file_name')
        }),
        ('Sharing Information', {
            'fields': ('owner_user_id', 'owner_user_email', 'shared_with_user_id', 'shared_with_user_email'),
            'classes': ('collapse',)
        }),
        ('Technical Information', {
            'fields': ('ip_address', 'user_agent', 'error_message'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(FolderLog)
class FolderLogAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user_email', 'action', 'folder_name', 
        'success', 'timestamp'
    ]
    list_filter = [
        'action', 'success', 'timestamp'
    ]
    search_fields = [
        'user_email', 'user_id', 'folder_name', 'folder_key'
    ]
    readonly_fields = [
        'id', 'timestamp'
    ]
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Main Information', {
            'fields': ('user_id', 'user_email', 'action', 'timestamp', 'success')
        }),
        ('Folder Details', {
            'fields': ('folder_key', 'folder_name', 'old_folder_name', 'parent_folder')
        }),
        ('Technical Information', {
            'fields': ('ip_address', 'user_agent', 'error_message'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False