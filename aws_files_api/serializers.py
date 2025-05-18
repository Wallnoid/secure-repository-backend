

# serializers.py
from rest_framework import serializers
from django.core.validators import RegexValidator





class UploadFileSerializer(serializers.Serializer):
    file_name = serializers.CharField(
        default='file.pdf',
        help_text='Only letters, numbers, spaces, hyphens and underscores are allowed',
        validators=[RegexValidator(r'^[a-zA-Z0-9\s_-]+\.[a-zA-Z0-9]+$', 'Only letters, numbers, spaces, hyphens and underscores are allowed')]
    )
    file = serializers.FileField(
        required=True,
    )


class CreateFolderSerializer(serializers.Serializer):
    folder_key = serializers.CharField(
        default='value',
        help_text='Only letters and numbers and spaces are allowed',
        validators=[RegexValidator(r'^[a-zA-Z0-9\s]+$', 'Only letters and numbers and spaces are allowed')]
    )

