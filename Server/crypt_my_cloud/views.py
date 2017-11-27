import codecs
import os

from django.core.exceptions import PermissionDenied
from django.db.models import Q
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
    get_object_or_404
)
from rest_framework.permissions import IsAuthenticated

from crypt_my_cloud.models import Key, File
from crypt_my_cloud.serializers import FileSerializer, FileLimitedSerializer


class FileView(CreateAPIView, RetrieveUpdateDestroyAPIView):
    serializer_class = FileSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return File.objects.select_related('key').filter(
            Q(owner=user) | Q(allowed_user__in=[user])
        )

    def get_object(self):
        obj = get_object_or_404(
            self.get_queryset(),
            file_name=self.request.query_params['file_name']
        )
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        serializer.save(
            key=Key.objects.create(key=codecs.encode(os.urandom(32), 'hex_codec').decode('ascii')),
            owner=self.request.user
        )

    def perform_destroy(self, instance):
        if self.request.user != instance.owner:
            raise PermissionDenied
        super(FileView, self).perform_destroy(instance)

    def perform_update(self, serializer):
        if self.request.user != serializer.instance.owner:
            raise PermissionDenied
        super(FileView, self).perform_update(serializer)



class FilesView(ListAPIView):
    serializer_class = FileLimitedSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return File.objects.select_related('key').filter(
            Q(owner=user) | Q(allowed_user__in=[user])
        )
