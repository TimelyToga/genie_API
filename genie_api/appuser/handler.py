from django.shortcuts import render
from django.db import transaction
import base64
import os

## Genie imports
from genie_api.common.json_shit import require_json_args, JsonResponse, JsonResponseBadRequest
from genie_api.appuser.models import User, Session
import genie_api.common.date as gdate
from genie_api.common.ids import generate

# Create your views here.
@require_json_args('guid')
def create_user(request):
    guid = request.json['guid']
    if(request.json.has_key('username')):
        username = request.json['username']
    else:
        username = ""

    ## TODO: Do some guid checking

    user = User.user_from_id(guid)
    if user:
        ## TODO: login user
        ## We know this is new user
        return JsonResponse({'reason': "user already exists", "guid": guid})

    with transaction.atomic():
        ## Create new user
        user = User(guid=guid)
        user.db_key = generate(User, 18, 'numeric')
        if username:
            user.username = username
        user.save()

        ## Create new Session
        session = Session()
        session.key = base64.urlsafe_b64encode(os.urandom(16))
        session.user = user
        session.created = gdate.datetime.utcnow()
        session.save()

    setattr(request, 'session', session)
    return JsonResponse(dict({'sid': session.pk}.items() + user.get_as_data(True).items()))

@require_json_args('guid')
def login(request):
    guid = request.json['guid']

    user = User.user_from_id(guid)
    if user:
        session = Session()
        session.key = base64.urlsafe_b64encode(os.urandom(16))
        session.user = user
        session.created = gdate.datetime.utcnow()
        session.save()

        return JsonResponse(dict({'sid': session.pk}.items() + user.get_as_data(True).items()))

    return JsonResponseBadRequest({"success": False})