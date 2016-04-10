from django import http, shortcuts, forms


def dashboard(request, **kwargs):
  class ASINForm(forms.Form):
    ASIN = forms.CharField(max_length=100)

  context = {'form': ASINForm()}
  return shortcuts.render(request, 'dashboard.html', context)
import models
import pprint
import trainer
from django import http, shortcuts


def search_handler(request, **kwargs):
  asin = kwargs['asin']
  product = models.Product.get_or_create_product(asin)
  response = http.HttpResponse()
  response.status_code = 200
  response.content_type = 'application/json'
  pprint.pprint(product.__dict__)
  for review in product.reviews.all():
    pprint.pprint(review.__dict__)
  return response

def train_handler(request, **kwargs):
  asin = kwargs['asin']
  training_set = trainer.train(asin)
  pprint.pprint(training_set.__dict__)
  product = models.Product.get_product(asin)
  pprint.pprint(product.__dict__)
  return http.HttpResponse()
