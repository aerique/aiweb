
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^profile/(?P<status>[a-zA-Z_]+)/$', views.profile, name='profile'),
    url(r'^replay/(?P<id>[a-zA-Z0-9_.]+)/$', views.replay, name='replay'),
]
