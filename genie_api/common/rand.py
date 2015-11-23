import string
import random


def rand_numeric_string(num_chars):
  return random_string(string.digits, num_chars)


def rand_alpha_string(num_chars):
  return random_string(string.ascii_lowercase, num_chars)


def rand_alphanumeric_string(num_chars):
  collection = string.ascii_lowercase + string.ascii_uppercase + string.digits
  return random_string(collection, num_chars)


def random_string(collection, num_chars):
  r = random.SystemRandom()
  return ''.join(r.choice(collection) for _ in xrange(num_chars))
