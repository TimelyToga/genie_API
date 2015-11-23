import datetime as pythondatetime

import genie_api.common.singleton as singleton
import pytz


class AbstractDate:

  def now(self):
    raise NotImplementedError

  def utcnow(self):
    raise NotImplementedError


class Date(AbstractDate):

  def utcnow(self):
    return pythondatetime.datetime.now(tz=pytz.utc)


class FakeDate(AbstractDate):

  def __init__(self, now):
    self._now = now

  def utcnow(self):
    return self._now


class DateFactory:
  __metaclass__ = singleton.Singleton

  def __init__(self):
    self._date = Date()

  def get_date(self):
    return self._date

  def set_date(self, date):
    self._date = date

  def reset_date(self):
    self._date = Date()

  # helpers
  def utcnow(self):
    return self._date.utcnow()

  # helpers
  def now(self):
    return self._date.now()


datetime = DateFactory()
