__author__ = 'Tim'

from django.conf.urls import include, url, patterns
from django.contrib import admin

urlpatterns = patterns('genie_api.appuser.handler',
    url(r'^/create$', 'create_user'),
    url(r'^/view/(?P<genre_name>.*)$', 'view_genre'),
    url(r'^/delete/(?P<genre_key>.*)$', 'delete_genre'),
    url(r'^/all$', 'all'),
)
