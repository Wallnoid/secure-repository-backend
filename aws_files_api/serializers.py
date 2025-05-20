# serializers.py
from rest_framework import serializers
from django.core.validators import RegexValidator





class UploadFileSerializer(serializers.Serializer):
    file_name = serializers.CharField(
        default='file.pdf',
        help_text='Only letters, numbers, spaces, hyphens, underscores and forward slashes are allowed. File must end with .pdf',
        validators=[RegexValidator(r'^[a-zA-Z0-9\s_\-/]+\.pdf$', 'Only letters, numbers, spaces, hyphens, underscores and forward slashes are allowed. File must end with .pdf')]
    )
    file = serializers.FileField(
        required=True,
    )


class CreateFolderSerializer(serializers.Serializer):
    folder_key = serializers.CharField(
        default='folder',
        help_text='Only letters and numbers and spaces are allowed',
        validators=[RegexValidator(r'^[a-zA-Z0-9\s_-]+$', 'Only letters and numbers and spaces and hyphens and underscores are allowed')]
    )

class FolderCrudSerializer(serializers.Serializer):
    folder_key = serializers.CharField(
        default='',
        help_text='Only letters and numbers and spaces and hyphens and underscores are allowed',
        validators=[RegexValidator(r'^[a-zA-Z0-9\s_\-/]+$', 'Only letters and numbers and spaces and hyphens and underscores are allowed')]
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

