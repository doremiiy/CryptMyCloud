import codecs
import os

from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveDestroyAPIView,
    get_object_or_404
)
from rest_framework.permissions import IsAuthenticated

from crypt_my_cloud.models import Key, File
from crypt_my_cloud.serializers import FileSerializer, FileLimitedSerializer


class FileView(CreateAPIView, RetrieveDestroyAPIView):

    serializer_class = FileSerializer
    permission_classes = (IsAuthenticated,)
    queryset =  File.objects.select_related('key').all()

    def get_object(self):
        obj = get_object_or_404(
            self.get_queryset(),
            file_name=self.request.query_params['file_name']
        )
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        serializer.save(key=Key.objects.create(
            key=codecs.encode(os.urandom(32), 'hex_codec').decode('ascii')
        ))

class FilesView(ListAPIView):

    serializer_class = FileLimitedSerializer
    permission_classes = (IsAuthenticated,)
    queryset = File.objects.all().order_by('file_name')