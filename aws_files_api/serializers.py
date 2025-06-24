# serializers.py
from rest_framework import serializers
from django.core.validators import RegexValidator


class UploadFileSerializer(serializers.Serializer):
    file_name = serializers.CharField(
        default='',
        help_text='Only letters, numbers, spaces, hyphens, underscores and forward slashes are allowed. File must end with .pdf or .bin',
        validators=[RegexValidator(r'^[a-zA-Z0-9\s_\-/]+$', 'Only letters, numbers, spaces, hyphens, underscores and forward slashes are allowed. File must end with .pdf or .bin')]
    )
    file = serializers.FileField(
        required=True,
    )
    
    def validate_file(self, value):
        """Validar archivo según extensión"""
        if value.name.lower().endswith('.bin'):
            # Validaciones específicas para archivos .bin
            if value.size > 50 * 1024 * 1024:  # 50MB
                raise serializers.ValidationError("El archivo .bin es demasiado grande (máximo 50MB)")
            if value.size == 0:
                raise serializers.ValidationError("El archivo .bin no puede estar vacío")
        else:
            raise serializers.ValidationError("El archivo debe tener extensión .bin")
        
        return value


class UpdateFileSerializer(serializers.Serializer):
    file_key = serializers.CharField(
        default='',
        help_text='Only letters, numbers, spaces, hyphens, underscores and forward slashes are allowed',
        validators=[RegexValidator(r'^[a-zA-Z0-9\s_\-/]+\.pdf$', 'Only letters, numbers, spaces, hyphens, underscores and forward slashes are allowed')]
    )
    
    new_file_key = serializers.CharField(
        default='',
        help_text='Only letters, numbers, spaces, hyphens, underscores and forward slashes are allowed',
        validators=[RegexValidator(r'^[a-zA-Z0-9\s_\-/]+$', 'Only letters, numbers, spaces, hyphens, underscores and forward slashes are allowed')]
    )
    

class DeleteFileSerializer(serializers.Serializer):
    file_key = serializers.CharField(
        default='',
        help_text='Only letters, numbers, spaces, hyphens, underscores and forward slashes are allowed',
        validators=[RegexValidator(r'^[a-zA-Z0-9\s_\-/]+\.pdf$', 'Only letters, numbers, spaces, hyphens, underscores and forward slashes are allowed')]
    )
    

class GetFilesByFolderSerializer(serializers.Serializer):
    folder_key = serializers.CharField(
        default='',
        help_text='Only letters and numbers and spaces and underscores are allowed',
        validators=[RegexValidator(r'^[a-zA-Z0-9\s_-]+$', 'Only letters and numbers and spaces and underscores are allowed')]
    )
    


class CreateFolderSerializer(serializers.Serializer):
    folder_key = serializers.CharField(
        default='',
        help_text='Only letters, numbers, spaces, hyphens, slashes, and underscores are allowed. Must NOT end with /',
        validators=[
            RegexValidator(
                r'^[a-zA-Z0-9\s_\-/]+$',
                'Only letters, numbers, spaces, slashes, hyphens, and underscores are allowed.'
            )
        ]
    )

    def validate_folder_key(self, value):
        if value.endswith('/'):
            raise serializers.ValidationError("Folder key must not end with '/'")
        return value


class FolderGetSerializer(serializers.Serializer):
    folder_key = serializers.CharField(
        default='',
        help_text='Only letters and numbers and spaces and hyphens and underscores are allowed',
        validators=[RegexValidator(r'^[a-zA-Z0-9\s_\-/]+$', 'Only letters and numbers and spaces and hyphens and underscores are allowed')]
    )
    

class UpdateFolderNameSerializer(serializers.Serializer):
    folder_key = serializers.CharField(
        default='',
        help_text='Only letters and numbers and spaces and hyphens and underscores are allowed',
        validators=[RegexValidator(r'^[a-zA-Z0-9\s_\-/]+$', 'Only letters and numbers and spaces and hyphens and underscores are allowed')]
    )
    new_folder_key = serializers.CharField(
        default='',
        help_text='Only letters and numbers and spaces and hyphens and underscores are allowed',
        validators=[RegexValidator(r'^[a-zA-Z0-9\s_\-/]+$', 'Only letters and numbers and spaces and hyphens and underscores are allowed')]
    )
    
    def validate_new_folder_key(self, value):
        if value.endswith('/'):
            raise serializers.ValidationError("New folder key must not end with '/'")
        return value
    
    def validate_folder_key(self, value):
        if value.endswith('/'):
            raise serializers.ValidationError("Folder key must not end with '/'")
        return value
    
    
    

class DeleteFolderSerializer(serializers.Serializer):
    folder_key = serializers.CharField(
        default='',
        help_text='Only letters and numbers and spaces and hyphens and underscores are allowed',
        validators=[RegexValidator(r'^[a-zA-Z0-9\s_\-]+$', 'Only letters and numbers and spaces and hyphens and underscores are allowed')]
    )


class DownloadFileSerializer(serializers.Serializer):
    file_key = serializers.CharField(
        default='',
            help_text='Only letters, numbers, spaces, hyphens, underscores and forward slashes are allowed',
        validators=[RegexValidator(r'^[a-zA-Z0-9\s_\-/]+\.pdf$', 'Only letters, numbers, spaces, hyphens, underscores and forward slashes are allowed')]
    )


class CreateBucketSerializer(serializers.Serializer):
    bucket_name = serializers.CharField(
        help_text='Bucket name for S3',
        validators=[RegexValidator(r'^[a-zA-Z0-9\s_\-]+$', 'Only letters, numbers, spaces, hyphens, and underscores are allowed')]
    )


class ResponseFileSerializer(serializers.Serializer):
    file_name = serializers.SerializerMethodField()
    file_key = serializers.CharField( source='Key')
    file_size = serializers.IntegerField( source='Size')
    file_last_modified = serializers.SerializerMethodField()
    
    def get_file_name(self, obj): 
        if obj['Key'].endswith('/'):
            return obj['Key'].split('/')[-2]
        else:
            return obj['Key'].split('/')[-1]
        
    def get_file_last_modified(self, obj):
        return obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S')

