try: import simplejson as json
except ImportError: import json
from functools import wraps
import collections

from django.http import HttpResponseRedirect
import genie_api.common.date
# import camoji.common.ids
# import camoji.thirdparty.twitter_web_oauth
# import camoji.cache.go
# import camoji.common.metrics
# import camoji.common.server
# import camoji.common.date
# import camoji.queue.defer
from genie_api.common.json_shit import HttpResponseUnauthorized, JsonResponseBadRequest


def memoize(function):
  memo = {}
  def wrapper(*args):
    if args in memo:
      return memo[args]
    else:
      rv = function(*args)
      memo[args] = rv
      return rv
  return wrapper


def update_user_agent_time_zone_if_needed(session, user_agent, time_zone):
  user_agent_sorted_string = json.dumps(collections.OrderedDict(sorted(user_agent.items())))
  if not session.user_agent or session.user_agent != user_agent_sorted_string:
    session.user_agent = user_agent_sorted_string
  if time_zone and (not session.time_zone or session.time_zone != str(time_zone)):
    session.time_zone = str(time_zone)
  session.used = genie_api.common.date.datetime.utcnow()
  session.save()


def timeme(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    with camoji.common.metrics.timing(str(func)):
      return func(*args, **kwargs)

  return wrapper


def require_session(func):
  @wraps(func)
  def wrapper(request):
    if not request.sid:
      return JsonResponseBadRequest('no sid')
    if not request.session:
      return HttpResponseUnauthorized()
    update_user_agent_time_zone_if_needed(request.session, request.user_agent, request.time_zone)
    return func(request)
  return wrapper


def if_session(func):
  @wraps(func)
  def wrapper(request):
    if not request.session:
      return func(request)
    update_user_agent_time_zone_if_needed(request.session, request.user_agent, request.time_zone)
    return func(request)
  return wrapper


def require_admin_session(func):
  @wraps(func)
  def wrapper(request, *args):
    if camoji.thirdparty.twitter_web_oauth.authenticated(request):
      if camoji.thirdparty.twitter_web_oauth.authorized(request):
        # go ahead!
        return func(request, *args)
      else:
        return HttpResponseRedirect('/a/denied')
    return camoji.thirdparty.twitter_web_oauth.authenticate(request)

  return wrapper