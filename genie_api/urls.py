"""genie_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url, patterns
from django.contrib import admin

import genie_api.main_handler as mh

urlpatterns = patterns('',
    url(r'^$', 'genie_api.main_handler.get_cookie'),
    url(r'^ok$', 'genie_api.main_handler.ok'),
    #url(r'^post', include('genie_api.post.urls')),
    url(r'^user', include('genie_api.appuser.urls')),

)