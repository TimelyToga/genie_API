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
        ## TODO: Signin user
        ## We know this is new user
        return JsonResponse({'reason': "user already exists", "guid": guid})

    with transaction.atomic():
        ## Create new user
        user = User(guid=guid)
        user.id = generate(User, 18, 'numeric')
        if username:
            user.username = username
        user.save()
        
        ## Create new Session
        session = Session()
        session.key = base64.urlsafe_b64encode(os.urandom(16))
        session.user = user
        session.created = gdate.datetime.utcnow()
        session.save()

    # setattr(request, 'session', session)
    ## return JsonResponse(dict({'sid': session.pk}.items() + user.get_all_user_as_data(user).items()))

    return JsonResponse(guid)

@require_json_args('guid')
def create_user2(request):
  email = request.json['email']
  username = request.json['username']
  password = request.json['password']

  if username != re.sub(r'[^a-zA-Z0-9_]+', '', username):
    return JsonResponseBadRequest('no valid username')

  normalized_email = camoji.common.normalize.normalize_email(email)
  if not normalized_email:
    logging.debug('no valid email')
    return JsonResponseBadRequest('no valid email')

  # check to see if this user is just trying to login
  user = User.user_from_username(username)
  possible_collision_status = USERNAME_TAKEN
  if not user:
    user = User.user_from_email(normalized_email)
    possible_collision_status = EMAIL_TAKEN

  if user:
    if user.authenticate(password):
      logging.info('Creating new session')
      session = Session()
      session.key = base64.urlsafe_b64encode(os.urandom(16))
      session.user = user
      session.created = camoji.common.date.datetime.utcnow()
      session.save()
      setattr(request, 'session', session)
      return JsonResponse(dict({'sid': session.pk}.items() + user.get_all_user_as_data(user).items()))
    return JsonResponse({'status': possible_collision_status})

  with transaction.atomic():
    # no existing user, create a new user with this information
    logging.info('Creating new user')
    user = User()
    user.key = common.ids.generate(User, 18, 'numeric')
    user.created = camoji.common.date.datetime.utcnow()
    user.username = username
    user.set_and_encrypt_password(password)
    user.update_email(normalized_email)
    user.save()
    logging.info('Creating new session')
    session = Session()
    session.key = base64.urlsafe_b64encode(os.urandom(16))
    session.user = user
    session.created = camoji.common.date.datetime.utcnow()
    session.save()

  setattr(request, 'session', session)

  return JsonResponse(dict({'sid': session.pk}.items() + user.get_all_user_as_data(user).items()))