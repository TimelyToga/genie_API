__author__ = 'Carlos Whitt'

try: import simplejson as json
except ImportError: import json
import logging
from django.http.response import HttpResponse
from django.http.response import HttpResponseBadRequest


class HttpResponseUnauthorized(HttpResponse):
  status_code = 401


def require_json_args(*args):
  def decorator(function):
    def wrapper(request):
      missing_args = []
      for arg in args:
        if arg not in request.json:
          missing_args += [arg]
      if missing_args:
        logging.warn('Missing args: %s' % missing_args)
        return JsonResponseBadRequest('Missing args: %s' % missing_args)
      return function(request)
    return wrapper
  return decorator


class JsonResponseBadRequest(HttpResponseBadRequest):
  def __init__(self, reason):
    super(JsonResponseBadRequest, self).__init__(json.dumps({'reason': reason}), content_type='application/json')


class JsonResponse(HttpResponse):
  def __init__(self, response):
    super(JsonResponse, self).__init__(json.dumps(response), content_type='application/json')
    self.raw_response = response
