import models
import pprint
from django import http, shortcuts


def search_handler(request, **kwargs):
  asin = kwargs['asin']
  product = models.Product.get_or_create_product(asin)
  response = http.HttpResponse()
  response.status_code = 200
  response.content_type = 'application/json'
  pprint.pprint(product.__dict__)
  return response


def dashboard(request, **kwargs):
  context = {}
  return shortcuts.render(request, 'dashboard.html', context)
