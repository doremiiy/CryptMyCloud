from django.conf.urls import url
from crypt_my_cloud import views


urlpatterns = [
    url(r'^$', views.FileView.as_view(), name='file'),
    url(r'^list/$', views.FilesView.as_view(), name = 'list')
]
