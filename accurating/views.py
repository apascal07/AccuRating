import logging
import pprint
import search
from django import shortcuts


def search_handler(request, **kwargs):
  product = search.get_product(kwargs['asin'])
  logging.info(pprint.pprint(product))
  context = {}
  return shortcuts.render(request, 'search.html', context)


def dashboard(request, **kwargs):
  context = {}
  return shortcuts.render(request, 'dashboard.html', context)
