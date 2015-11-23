from django.db.models import CharField, DateField, DateTimeField, ForeignKey, IntegerField
from django.db import models

from django.core.exceptions import ObjectDoesNotExist
import json

import genie_api.common.date

# Create your models here.

class User(models.Model):

    class Meta:
        ordering = ('created',)

    guid = IntegerField(primary_key=True, unique=True, auto_created=True)
    created = DateTimeField(auto_now=True)
    username = CharField(max_length=128, db_index=True)

    @staticmethod
    def user_from_id(user_id):
        try:
            return User.objects.get(guid__iexact=user_id)
        except ObjectDoesNotExist:
            return None

class Session(models.Model):
  class Meta:
    db_table = 'camoji_session'

  key = models.CharField(primary_key=True, max_length=256)
  user = models.ForeignKey(User, related_name='+')
  user_agent = models.CharField(null=True, max_length=512)
  time_zone = models.CharField(null=True, max_length=512)
  created = models.DateTimeField('created', db_index=True)
  used = models.DateTimeField('used', null=True, db_index=True)
  deleted = models.BooleanField(default=False)


  def app_version(self):
    if not self.user_agent:
      return None
    return json.loads(str(self.user_agent))['app_version']

  def invalidate(self):
    self.deleted = True
    self.save()

  @staticmethod
  def invalidate_for_user(user, except_sessions=list()):
    except_sessions = set(except_sessions)
    # make sure all exception session are valid
    for session in except_sessions:
      if session.deleted:
        # if any are not valid, bail on entire request
        return
    latest_created = None
    for except_session in except_sessions:
      if not latest_created or except_session.created > latest_created:
        latest_created = except_session.created
    for session in Session.objects.filter(user=user, deleted=False):
      if session in except_sessions:
        # do not touch any sessions passed in except
        continue

      if session.created < latest_created:
        # logging.info('invalidating session: %s and user: %s, %s' % (session.pk, user.pk, session.user_agent))
        session.invalidate()
        continue

      if not session.used:
        #logging.info('invalidating session: %s and user: %s, %s' % (session.pk, user.pk, session.user_agent))
        session.invalidate()
        continue

      # session was created after but hasn't been used in 10 minutes
      hour_old = genie_api.common.date.datetime.utcnow() - genie_api.common.date.datetime.timedelta(minutes=10)
      if session.used < hour_old:
        ## logging.info('invalidating session: %s and user: %s, %s' % (session.pk, user.pk, session.user_agent))
        session.invalidate()
        continue