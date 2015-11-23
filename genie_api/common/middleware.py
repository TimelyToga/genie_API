try: import simplejson as json
except ImportError: import json
import logging
import datetime
import collections
import uuid
import traceback
import sys
import time

from pytz import timezone
import re
#from raven.contrib.django.models import client as sentry
from django.conf import settings
from django.utils.cache import patch_vary_headers
from django.utils.http import cookie_date
from django.utils.importlib import import_module
from django.http import HttpResponsePermanentRedirect, HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from genie_api.common.json_shit import JsonResponseBadRequest
from genie_api.common.server import set_json_on_request
from genie_api.appuser.models import Session

# import genie_api.common.server
import genie_api.settings
import genie_api.common.decorators
# import genie_api.thirdparty.twitter_web_oauth


class ProcessExceptionMiddleware(object):
  def process_response(self, request, response):
    logging.debug('MIDDLEWARE: ProcessExceptionMiddleware:process_response')
    if response.status_code and int(response.status_code) >= 500:
      logging.error('\n'.join(traceback.format_exception(*sys.exc_info())))
      # sentry.captureException(extra={
      #  'user-agent': request.META.get('HTTP_USER_AGENT', '')
      #})
    return response


XS_SHARING_ALLOWED_ORIGINS = '*'
XS_SHARING_ALLOWED_METHODS = ['POST', 'GET', 'OPTIONS', 'PUT', 'DELETE']
XS_SHARING_ALLOWED_HEADERS = ['Content-Type', '*']
XS_SHARING_ALLOWED_CREDENTIALS = 'true'


class XsSharingMiddleware(object):
  def process_request(self, request):
    logging.debug('MIDDLEWARE: XsSharingMiddleware:process_request')
    if 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META:
      response = HttpResponse()
      response['Access-Control-Allow-Origin'] = XS_SHARING_ALLOWED_ORIGINS
      response['Access-Control-Allow-Methods'] = ",".join(XS_SHARING_ALLOWED_METHODS)
      response['Access-Control-Allow-Headers'] = ",".join(XS_SHARING_ALLOWED_HEADERS)
      response['Access-Control-Allow-Credentials'] = XS_SHARING_ALLOWED_CREDENTIALS
      return response

    return None

  def process_response(self, request, response):
    logging.debug('MIDDLEWARE: XsSharingMiddleware:process_response')
    response['Access-Control-Allow-Origin'] = XS_SHARING_ALLOWED_ORIGINS
    response['Access-Control-Allow-Methods'] = ",".join(XS_SHARING_ALLOWED_METHODS)
    response['Access-Control-Allow-Headers'] = ",".join(XS_SHARING_ALLOWED_HEADERS)
    response['Access-Control-Allow-Credentials'] = XS_SHARING_ALLOWED_CREDENTIALS

    return response


def get_response_params(response):
  if hasattr(response, 'raw_response'):
    return response.raw_response
  return {}


def get_request_params(request):
  try:
    if request.method == 'GET':
      return None
    if not request.json:
      return None
    request_json = dict.copy(request.json)
    if 'password' in request_json:
      del request_json['password']
    if 'contacts' in request_json:
      del request_json['contacts']
    return request_json
  except:
    return {}


class JsonOnRequestMiddleware(object):
  def process_request(self, request):
    try:
      genie_api.common.server.set_json_on_request(request)
    except:
      return JsonResponseBadRequest('bad json')


IOS_USER_AGENT_PATTERN = re.compile(r'(.*)/(.*) \((.*); iOS (.*);.*\)')


class HeaderOnRequestMiddleware(object):
  def _parse_user_agent(self, user_agent):
    m = IOS_USER_AGENT_PATTERN.match(str(user_agent))
    if m:
      return {
        'os': 'ios',
        'os_version': m.group(4),
        'device_model': m.group(3),
        'app_version': m.group(2),
        'app': m.group(1)
      }
    return {}

  def process_request(self, request):
    time_zone = timezone(request.META.get('HTTP_TIME_ZONE')) if request.META.get('HTTP_TIME_ZONE') else None
    setattr(request, 'time_zone', time_zone)
    setattr(request, 'user_agent', self._parse_user_agent(request.META.get('HTTP_USER_AGENT')))
    setattr(request, 'app_version', int(request.user_agent['app_version']) if 'app_version' in request.user_agent else None)


class SidOnRequestMiddleware(object):
  def process_request(self, request):
    sid = request.META.get('HTTP_SID')
    if not sid and hasattr(request, 'json'):
      sid = request.json.get('sid')
    setattr(request, 'sid', sid)


class SessionOnRequestMiddleware(object):
  def process_request(self, request):
    session = None
    if request.sid:
      try:
        session = Session.objects.get(pk=request.sid)
      except ObjectDoesNotExist:
        pass
    setattr(request, 'session', session)


class LoggingMiddleware(object):
  def process_request(self, request):
    logging.debug('MIDDLEWARE: RequestTimeLoggingMiddleware:process_request')
    try:
      request_params = get_request_params(request)
      dt = datetime.datetime.utcnow()
      if not hasattr(request, '_logging_uuid'):
        request._logging_uuid = uuid.uuid1()
        request._logging_start_dt = dt

      username = request.session.user.username if hasattr(request, 'session') and request.session and hasattr(request.session, 'user') else None
      if not username and hasattr(request, 'web_session'):
        username = camoji.thirdparty.twitter_web_oauth.username(request)

      logging.debug(
        u'\n%-8s %s @%s --> %s -> %s on %s' % (
          'APIREQUEST' if request.path.startswith('/_/') else 'WEBREQUEST',
          request.sid if hasattr(request, 'sid') else None,
          username,
          request.path,
          json.dumps(collections.OrderedDict(sorted(request_params.items()))) if request_params else 'none',
          request.META['HTTP_USER_AGENT'] if 'HTTP_USER_AGENT' in request.META else 'unknown'
        )
      )
    except:
      logging.exception('issue logging request')

  def process_response(self, request, response):
    logging.debug('MIDDLEWARE: RequestTimeLoggingMiddleware:process_response')
    try:
      dt = datetime.datetime.utcnow()
      if not hasattr(request, '_logging_uuid'):
        request._logging_uuid = uuid.uuid1()
        request._logging_start_dt = dt
      s = getattr(response, 'status_code', 0)
      status_code = str(s)
      if s in (300, 301, 302, 307):
        status_code += ' => %s' % response.get('Location', '?')
      elif not response.streaming and response.content:
        status_code += ' (%db)' % len(response.content)
      request_params = get_request_params(request)
      response_params = None
      if s != 200:
        response_params = get_response_params(response)
      version = request.user_agent['app_version'] if request.user_agent else None
      in_session = bool(hasattr(request, 'session') and request.session)
      username = request.session.user.username if hasattr(request, 'session') and request.session and hasattr(request.session, 'user') else None
      if not username and hasattr(request, 'web_session'):
        username = camoji.thirdparty.twitter_web_oauth.username(request)

      if in_session:
        logging.debug(
          u'\n%-8s %s @%s v%s <-- %s %s %s ==> %s +%s' % (
            'APIRESPONSE' if request.path.startswith('/_/') else 'WEBRESPONSE',
            request.sid if hasattr(request, 'sid') else None,
            username,
            request.user_agent['app_version'] if request.user_agent else None,
            status_code,
            request.path,
            json.dumps(collections.OrderedDict(sorted(request_params.items()))) if request_params else 'none',
            json.dumps(collections.OrderedDict(sorted(response_params.items()))) if response_params else 'none',
            dt - request._logging_start_dt,
          )
        )
      elif version:
        logging.debug(
          u'\n%-8s v%s <-- %s %s %s ==> %s +%s' % (
            'APIRESPONSE' if request.path.startswith('/_/') else 'WEBRESPONSE',
            request.user_agent['app_version'] if request.user_agent else None,
            status_code,
            request.path,
            json.dumps(collections.OrderedDict(sorted(request_params.items()))) if request_params else 'none',
            json.dumps(collections.OrderedDict(sorted(response_params.items()))) if response_params else 'none',
            dt - request._logging_start_dt,
          )
        )
      else:
        logging.debug(
          u'\n%-8s <-- %s %s %s ==> %s +%s' % (
            'APIRESPONSE' if request.path.startswith('/_/') else 'WEBRESPONSE',
            status_code,
            request.path,
            json.dumps(collections.OrderedDict(sorted(request_params.items()))) if request_params else 'none',
            json.dumps(collections.OrderedDict(sorted(response_params.items()))) if response_params else 'none',
            dt - request._logging_start_dt,
          )
        )
    except:
      logging.exception('issue logging response')
      # sentry.captureException()
    return response


class SSLifyMiddleware(object):
  def process_request(self, request):
    logging.debug('MIDDLEWARE: SSLifyMiddleware:process_request')
    if not any((genie_api.settings.DEBUG, genie_api.settings.STAGING, request.is_secure())):
      url = request.build_absolute_uri(request.get_full_path())
      secure_url = url.replace('http://', 'https://')
      return HttpResponsePermanentRedirect(secure_url)


class WebSessionMiddleware(object):
  def process_request(self, request):
    logging.debug('inside WebSessionMiddleware')
    engine = import_module(settings.SESSION_ENGINE)
    session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
    request.web_session = engine.SessionStore(session_key)

  def process_response(self, request, response):
    """
    If request.web_session was modified, or if the configuration is to save the
    session every time, save the changes and set a session cookie.
    """
    try:
      accessed = request.web_session.accessed
      modified = request.web_session.modified
    except AttributeError:
      pass
    else:
      if accessed:
        patch_vary_headers(response, ('Cookie',))
      if modified or settings.SESSION_SAVE_EVERY_REQUEST:
        if request.web_session.get_expire_at_browser_close():
          max_age = None
          expires = None
        else:
          max_age = request.web_session.get_expiry_age()
          expires_time = time.time() + max_age
          expires = cookie_date(expires_time)
        # Save the session data and refresh the client cookie.
        # Skip session save for 500 responses, refs #3881.
        if response.status_code != 500:
          request.web_session.save()
          response.set_cookie(settings.SESSION_COOKIE_NAME,
                              request.web_session.session_key, max_age=max_age,
                              expires=expires, domain=settings.SESSION_COOKIE_DOMAIN,
                              path=settings.SESSION_COOKIE_PATH,
                              secure=settings.SESSION_COOKIE_SECURE or None,
                              httponly=settings.SESSION_COOKIE_HTTPONLY or None)
    return response



class SubdomainURLRoutingMiddleware(object):
  def process_request(self, request):    
    full_host = request.get_host()
    if full_host == genie_api.settings.WWW_NAKED_HOST:
      subdomain = 'www'
    else:
      subdomain = full_host.split('.')[0]

    urlconf = camoji.settings.SUBDOMAIN_URLCONFS.get(subdomain)
    logging.debug('Using urlconf %s for subdomain: %s', repr(urlconf), repr(subdomain))
    request.urlconf = urlconf
