import logging
try: import simplejson as json
except ImportError: import json


def set_json_on_request(request):
  if request.method == 'GET':
    return
  if hasattr(request, 'json'):
    return
  legacy = False
  try:
    if request.POST:
      if 'json' in request.POST:
        params = json.loads(request.POST['json'])
      else:
        legacy = True
        params = request.POST.dict()
    else:
      params = None
      if request.META.get('REQUEST_METHOD', '') == 'POST':
        params = json.loads(request.body)
      if not params:
        if request.GET:
          # TODO(carlos): fix the docs version but they submit a POST with get params, likely using request.DATA
          params = request.GET.dict()
        else:
          params = json.loads(request.body)
    setattr(request, 'json', params)
  except:
    logging.info('invalidjson - invalid json for post: %s, path: %s, legacy: %s' % (bool(request.POST), request.path, legacy))
    raise Exception('errorlog - invalid json for post: %s, path: %s, legacy: %s' % (bool(request.POST), request.path, legacy))
