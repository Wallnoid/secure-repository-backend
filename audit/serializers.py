from rest_framework import serializers
from .models import FileLog, FolderLog


class FileLogSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = FileLog
        fields = [
            'id', 'user_id', 'user_email', 'action', 'action_display',
            'file_key', 'file_name', 'file_size',
            'owner_user_id', 'owner_user_email', 'shared_with_user_id',
            'shared_with_user_email', 'old_file_name', 'ip_address',
            'user_agent', 'timestamp', 'success', 'error_message'
        ]
        read_only_fields = ['id', 'timestamp', 'action_display']


class FolderLogSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = FolderLog
        fields = [
            'id', 'user_id', 'user_email', 'action', 'action_display',
            'folder_key', 'folder_name', 'old_folder_name',
            'parent_folder', 'ip_address', 'user_agent', 'timestamp',
            'success', 'error_message'
        ]
        read_only_fields = ['id', 'timestamp', 'action_display']


class FileLogFilterSerializer(serializers.Serializer):
    file_key = serializers.CharField(required=False, help_text="File key")
    action = serializers.ChoiceField(
        choices=FileLog.ACTION_CHOICES,
        required=False,
        help_text="Action performed"
    )
    start_date = serializers.DateTimeField(required=False, help_text="Start date")
    end_date = serializers.DateTimeField(required=False, help_text="End date")
    limit = serializers.IntegerField(default=100, min_value=1, max_value=1000, help_text="Results limit")


class FolderLogFilterSerializer(serializers.Serializer):
    folder_key = serializers.CharField(required=False, help_text="Folder key")
    action = serializers.ChoiceField(
        choices=FolderLog.ACTION_CHOICES,
        required=False,
        help_text="Action performed"
    )
    start_date = serializers.DateTimeField(required=False, help_text="Start date")
    end_date = serializers.DateTimeField(required=False, help_text="End date")
    limit = serializers.IntegerField(default=100, min_value=1, max_value=1000, help_text="Results limit")


class FileAuditRequestSerializer(serializers.Serializer):
    file_key = serializers.CharField(required=True, help_text="File key")
    
    def validate_file_key(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("File key cannot be empty")
        
        if len(value) > 1024:
            raise serializers.ValidationError("File key is too long")
        
        return value.strip()


class AllFilesAuditRequestSerializer(serializers.Serializer):
    pass


class FolderFilesAuditRequestSerializer(serializers.Serializer):
    key_folder = serializers.CharField(required=False, allow_blank=True, help_text="Folder key/path (empty for root)")
    
    def validate_key_folder(self, value):
        if value is None:
            value = ""
        
        if len(value) > 1024:
            raise serializers.ValidationError("Folder key is too long")
        
        value = value.strip()
        
        if not value:
            return ""
        
        if not value.endswith('/'):
            value += '/'
            
        return value


class FileReportRequestSerializer(serializers.Serializer):
    pass


class FolderReportRequestSerializer(serializers.Serializer):
    pass


class S3MetadataSerializer(serializers.Serializer):
    file_size = serializers.IntegerField(allow_null=True)
    last_modified = serializers.CharField(allow_null=True)
    etag = serializers.CharField(allow_null=True)
    content_type = serializers.CharField(allow_null=True)
    metadata = serializers.DictField(allow_null=True)
    storage_class = serializers.CharField(allow_null=True)
    server_side_encryption = serializers.CharField(allow_null=True)
    version_id = serializers.CharField(allow_null=True)
    object_size = serializers.IntegerField(allow_null=True)
    checksum = serializers.DictField(allow_null=True)
    creation_date = serializers.CharField(allow_null=True)
    error = serializers.CharField(required=False)


class SharedWithUserSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    user_email = serializers.EmailField()
    shared_at = serializers.CharField()
    sharing_id = serializers.IntegerField()


class OwnerInfoSerializer(serializers.Serializer):
    owner_user_id = serializers.CharField()
    owner_user_email = serializers.EmailField()
    file_name = serializers.CharField()
    file_size_db = serializers.IntegerField(allow_null=True)


class SharedInfoSerializer(serializers.Serializer):
    is_shared = serializers.BooleanField()
    shared_count = serializers.IntegerField()
    shared_with = SharedWithUserSerializer(many=True)
    error = serializers.CharField(required=False)


class FileAuditResponseSerializer(serializers.Serializer):
    file_key = serializers.CharField()
    bucket_name = serializers.CharField()
    file_metadata = serializers.DictField()
    shared_info = serializers.ListField()
    owner_info = serializers.DictField()
    audit_timestamp = serializers.CharField()


class AllFilesAuditResponseSerializer(serializers.Serializer):
    files_audit = serializers.ListField()
    total_files = serializers.IntegerField()
    audit_timestamp = serializers.CharField() 