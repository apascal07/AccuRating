from django import http, shortcuts, forms


def dashboard(request, **kwargs):
  class ASINForm(forms.Form):
    ASIN = forms.CharField(max_length=100)

  context = {'form': ASINForm()}
  return shortcuts.render(request, 'dashboard.html', context)
import models
import pprint
import trainer
import verifier
import json
from django import http, shortcuts


def search_handler(request, **kwargs):
  pprint.pprint([p.asin for p in models.Product.objects.all()])
  asin = kwargs['asin']
  product = models.Product.get_or_create_product(asin)
  response = http.HttpResponse()
  response.status_code = 200
  response.content_type = 'application/json'
  pprint.pprint(product.__dict__)
  # for review in product.reviews.all():
  #   pprint.pprint(review.__dict__)
  return response


def train_handler(request, **kwargs):
  trainer_ = trainer.Trainer()
  ps = [p.asin for p in models.Product.objects.all()]
  tset = trainer_.train(ps)
  pprint.pprint(tset.__dict__)
  for p in ps:
    pro = models.Product.get_product(p)
    print 'amaz: {}, avg: {}, smart: {}'.format(pro.amazon_rating, pro.average_rating, pro.weighted_rating)
  return http.HttpResponse()


def verification_handler(request):
  asins = [p.asin for p in models.Product.objects.all()]
  return http.HttpResponse(str(verifier.verify(asins)))
