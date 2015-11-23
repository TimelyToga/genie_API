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

from urlmiddleware.conf import middleware, mpatterns

from genie_api.common.middleware import SessionOnRequestMiddleware, SidOnRequestMiddleware, JsonOnRequestMiddleware



import genie_api.handler as mh

middlewarepatterns = mpatterns('',
    middleware(r'^.*$', JsonOnRequestMiddleware),
    middleware(r'^.*$', SidOnRequestMiddleware),
    middleware(r'^.*$', SessionOnRequestMiddleware),
)

urlpatterns = patterns('',
    url(r'^$', 'genie_api.handler.get_cookie'),
    url(r'^ok$', 'genie_api.handler.ok'),
    #url(r'^post', include('genie_api.post.urls')),
    url(r'^user', include('genie_api.appuser.urls')),

)