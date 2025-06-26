from rest_framework import serializers


class FileAuditRequestSerializer(serializers.Serializer):
    file_key = serializers.CharField(
        help_text='Clave del archivo en S3 para obtener información de auditoría'
    )


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
    bucket_name_db = serializers.CharField()


class SharedInfoSerializer(serializers.Serializer):
    is_shared = serializers.BooleanField()
    shared_count = serializers.IntegerField()
    shared_with = SharedWithUserSerializer(many=True)
    error = serializers.CharField(required=False)


class FileAuditResponseSerializer(serializers.Serializer):
    file_key = serializers.CharField()
    bucket_name = serializers.CharField()
    s3_metadata = S3MetadataSerializer()
    shared_info = SharedInfoSerializer()
    owner_info = OwnerInfoSerializer(allow_null=True)
    audit_timestamp = serializers.CharField()
    error = serializers.CharField(required=False)


class AllFilesAuditResponseSerializer(serializers.Serializer):
    files_audit = FileAuditResponseSerializer(many=True)
    total_files = serializers.IntegerField()
    audit_timestamp = serializers.CharField() 