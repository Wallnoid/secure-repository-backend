from django.db import models
from django.utils import timezone

class FileLog(models.Model):
    ACTION_CHOICES = [
        ('UPLOAD', 'Upload'),
        ('DOWNLOAD', 'Download'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('SHARE', 'Share'),
        ('UNSHARE', 'Unshare'),
    ]
    
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=255, help_text="ID of the user who performed the action")
    user_email = models.CharField(max_length=255, help_text="Email of the user who performed the action")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, help_text="Action performed")
    file_key = models.TextField(help_text="File key/path in S3")
    file_name = models.CharField(max_length=255, help_text="File name")
    file_size = models.BigIntegerField(null=True, blank=True, help_text="File size in bytes")
    bucket_name = models.CharField(max_length=255, help_text="S3 bucket name")
    
    owner_user_id = models.CharField(max_length=255, null=True, blank=True, help_text="ID of the file owner (if shared)")
    owner_user_email = models.CharField(max_length=255, null=True, blank=True, help_text="Email of the file owner (if shared)")
    shared_with_user_id = models.CharField(max_length=255, null=True, blank=True, help_text="ID of the user the file was shared with")
    shared_with_user_email = models.CharField(max_length=255, null=True, blank=True, help_text="Email of the user the file was shared with")
    
    old_file_name = models.CharField(max_length=255, null=True, blank=True, help_text="Previous file name (for update operations)")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="User's IP address")
    user_agent = models.TextField(null=True, blank=True, help_text="Browser user agent")
    
    timestamp = models.DateTimeField(default=timezone.now, help_text="Date and time of the action")
    success = models.BooleanField(default=True, help_text="Indicates if the operation was successful")
    error_message = models.TextField(null=True, blank=True, help_text="Error message if the operation failed")
    
    class Meta:
        db_table = 'audit_file_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user_id', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['file_key']),
            models.Index(fields=['bucket_name', 'timestamp']),
        ]
    
    def __str__(self):
        if self.shared_with_user_id:
            return f"{self.user_email} {self.get_action_display().lower()} {self.file_name} (shared with {self.shared_with_user_email}) - {self.timestamp}"
        return f"{self.user_email} {self.get_action_display().lower()} {self.file_name} - {self.timestamp}"


class FolderLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    ]
    
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=255, help_text="ID of the user who performed the action")
    user_email = models.CharField(max_length=255, help_text="Email of the user who performed the action")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, help_text="Action performed")
    folder_key = models.TextField(help_text="Folder key/path in S3")
    folder_name = models.CharField(max_length=255, help_text="Folder name")
    bucket_name = models.CharField(max_length=255, help_text="S3 bucket name")
    
    old_folder_name = models.CharField(max_length=255, null=True, blank=True, help_text="Previous folder name (for update operations)")
    parent_folder = models.CharField(max_length=255, null=True, blank=True, help_text="Parent folder")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="User's IP address")
    user_agent = models.TextField(null=True, blank=True, help_text="Browser user agent")
    
    timestamp = models.DateTimeField(default=timezone.now, help_text="Date and time of the action")
    success = models.BooleanField(default=True, help_text="Indicates if the operation was successful")
    error_message = models.TextField(null=True, blank=True, help_text="Error message if the operation failed")
    
    class Meta:
        db_table = 'audit_folder_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user_id', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['folder_key']),
            models.Index(fields=['bucket_name', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user_email} {self.get_action_display().lower()} folder {self.folder_name} - {self.timestamp}"
