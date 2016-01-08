__author__ = 'Tim'

from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.core.context_processors import csrf
from django.shortcuts import render_to_response, render

import django.conf.urls
import json

def index(request):
    return render(request, 'theme.html', {})

def about(request):
    return render(request, 'about.html', {})

def get_cookie(request):
    c = {}
    c.update(csrf(request))
    s = request.session
    return HttpResponse(c['csrf_token'], s)

def ok(request):
    return HttpResponse(json.dumps("ok"))