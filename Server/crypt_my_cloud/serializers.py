from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from crypt_my_cloud.models import File


class FileSerializer(serializers.ModelSerializer):

    key = serializers.SlugRelatedField(slug_field='key', read_only=True)
    owner = serializers.ReadOnlyField(source='owner.username')
    allowed_user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.exclude(username=owner),
        allow_null=True,
        many=True
    )

    class Meta:
        model = File
        fields = ('allowed_user', 'file_name', 'key', 'owner',)
        read_only_fields = ('key', 'owner',)

    def update(self, instance, validated_data):
        instance = super(FileSerializer, self).update(instance, validated_data)
        allowed_user = (
            validated_data.pop('allowed_user') if validated_data.get('allowed_user') else []
        )
        if instance.owner in allowed_user:
            raise ValidationError('Cannot share file with the owner.')
        instance.allowed_user.remove(*(set(instance.allowed_user.all()) - set(allowed_user)))
        instance.allowed_user.add(*(set(allowed_user) - set(instance.allowed_user.all())))
        return instance


class FileLimitedSerializer(serializers.ModelSerializer):

    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = File
        fields = ('file_name', 'owner')
        read_only_fields = ('file_name', 'owner')
