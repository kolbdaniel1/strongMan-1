from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.server_connections, name='server_connections'),
]
