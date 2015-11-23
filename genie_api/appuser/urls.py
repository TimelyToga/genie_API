__author__ = 'Tim'

from django.conf.urls import include, url, patterns
from django.contrib import admin

urlpatterns = patterns('genie_api.appuser.handler',
    url(r'^/create$', 'create_user'),
    url(r'^/login', 'login'),
    url(r'^/all$', 'all'),
)
