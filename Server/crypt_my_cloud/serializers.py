from rest_framework import serializers

from crypt_my_cloud.models import File

class FileSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = ('file_name', 'key')
        read_only_fields = ('key',)