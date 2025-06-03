from rest_framework import serializers
from shared_files.models import SharedFile

class SharedUserSerializer(serializers.Serializer):
    id = serializers.CharField()
    email = serializers.CharField()

class SharedFileSerializer(serializers.ModelSerializer):
    file_key = serializers.CharField()
    file_name = serializers.CharField()
    file_size = serializers.IntegerField()
    shared_with_users = SharedUserSerializer(many=True)

    class Meta:
        model = SharedFile
        fields = ('file_key', 'file_name', 'file_size', 'shared_with_users')


class DeleteSharedFileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = SharedFile
        fields = ('id',)


class GetSharedFilesSerializer(serializers.ModelSerializer):
    shared_with_users = SharedUserSerializer(many=True)

    class Meta:
        model = SharedFile
        fields = ('shared_with_users',)


class GetSharedFilesByFileKeySerializer(serializers.ModelSerializer):
    file_key = serializers.CharField()

    class Meta:
        model = SharedFile
        fields = ('file_key',)


