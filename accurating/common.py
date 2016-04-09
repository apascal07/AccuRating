import logging
import math
import time
import urllib
import urlparse


def update_url(url, parameters, append=True):
  """Updates the given URL to include (add/replace) the given parameters."""
  if not parameters:
    return url
  # extract any existing parameters in the URL
  url = urllib.unquote(url)
  # update the parameter dictionary with the old parameters
  if append:
    parsed_url = urlparse.urlparse(url)
    old_parameters = dict(urlparse.parse_qsl(parsed_url.query))
    parameters.update(old_parameters)
  # encode the parameter query string and recreate the full URL again
  query = urllib.urlencode(old_parameters)
  base_url = url.split('?')[0]
  new_url = '{}?{}'.format(base_url, query)
  return new_url


def timer(fn):
  """Clocks the time it takes a function to execute."""
  def wrapper(*args, **kwargs):
    start = time.time()
    result = fn(*args, **kwargs)
    end = time.time()
    delta = end - start
    print 'Executed {} in {} sec(s).'.format(fn.__name__, delta)
    return result
  return wrapper
