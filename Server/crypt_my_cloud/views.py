from rest_framework.generics import CreateAPIView, RetrieveAPIView, get_object_or_404

from crypt_my_cloud.models import File
from crypt_my_cloud.serializers import FileSerializer


class FileView(CreateAPIView, RetrieveAPIView):
    serializer_class = FileSerializer
    queryset =  File.objects.all()

    def get_object(self):
        obj = get_object_or_404(
            self.get_queryset(),
            file_name=self.request.query_params['file_name']
        )
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        # TODO: generate real key here
        serializer.save(key='test_key')
