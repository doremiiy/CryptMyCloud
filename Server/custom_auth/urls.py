from django.conf.urls import url
from custom_auth import views


urlpatterns = [
    url(r'^list/$', views.UsersView.as_view(), name='list'),
]
