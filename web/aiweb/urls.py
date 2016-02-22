
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^mission/$', views.mission, name='mission'),
    url(r'^submission/', views.submission, name='submission'),
    url(r'^result/(?P<username>[a-zA-Z0-9_.\-]+)/', views.result_page, name='result'),
    url(r'^result/', views.result_page, name='result'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^profile/(?P<status>[a-zA-Z_.]+)/$', views.profile, name='profile'),
    url(r'^replay/(?P<id>[a-zA-Z0-9_.]+)/$', views.replay, name='replay'),
    url(r'^report/(?P<id>[a-zA-Z0-9_.\-]+)/$', views.report, name='report'),
    url(r'^(?P<gamename>[a-zA-Z0-9_.]+)/rank/$', views.rank, name='rank'),
    url(r'^(?P<gamename>[a-zA-Z0-9_.]+)/results/$', views.match_results, name='results'),
    url(r'^(?P<gamename>[a-zA-Z0-9_.]+)/info/$', views.game_info, name='game_info'),
    url(r'^(?P<gamename>[a-zA-Z0-9_.]+)/problem/$', views.problem_description, name='problem_description'),
    url(r'^(?P<gamename>[a-zA-Z0-9_.]+)/starter/$', views.starter_packages, name='starter_packages'),
]
