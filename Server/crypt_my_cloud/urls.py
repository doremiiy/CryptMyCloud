from django.conf.urls import url
from crypt_my_cloud import views


urlpatterns = [  # pylint: disable=invalid-name
    url(
        r'^file/$',
        views.FileView.as_view(),
        name='file'
    )
]
