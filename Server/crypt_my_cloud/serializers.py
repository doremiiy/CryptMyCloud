from rest_framework import serializers

from crypt_my_cloud.models import File


class FileSerializer(serializers.ModelSerializer):

    key = serializers.SlugRelatedField(slug_field='key', read_only=True)
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = File
        fields = ('file_name', 'key', 'owner',)
        read_only_fields = ('key', 'owner',)


class FileLimitedSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = ('file_name',)
        read_only_fields = ('file_name',)