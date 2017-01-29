# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    # например, /api/v1/
    url(r'^$', views.index, name='api-index'),
    # например, /api/v1/someapp.person/
    url(r'^(?P<model>[\w\.]+)/$', views.dispatcher, name='api-model'),
    # например, /api/v1/someapp.person/1/
    url(r'^(?P<model>[\w\.]+)/(?P<pk>[\d]+)/$', views.object_dispatcher, name='api-object'),
]
