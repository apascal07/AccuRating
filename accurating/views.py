import logging
import pprint
import search
import json
from django import http, shortcuts


def search_handler(request, **kwargs):
  product = search.get_product(kwargs['asin'])
  response = http.HttpResponse()
  response.status_code = 200
  response.content_type = 'application/json'
  pprint.pprint(product.__dict__)
  return response


def dashboard(request, **kwargs):
  context = {}
  return shortcuts.render(request, 'dashboard.html', context)
