from rest_framework import serializers

from crypt_my_cloud.models import File, Key


class KeySerializer(serializers.ModelSerializer):
    # TODO: remove this serializer if it's still useless
    class Meta:
        model = Key
        fields = ('key', )
        read_only_fields = ('key',)


class FileSerializer(serializers.ModelSerializer):

    #key=KeySerializer(read_only=True)
    key = serializers.SlugRelatedField(slug_field='key', read_only=True)

    class Meta:
        model = File
        fields = ('file_name', 'key')
        read_only_fields = ('key',)


class FileLimitedSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = ('file_name',)
        read_only_fields = ('file_name',)