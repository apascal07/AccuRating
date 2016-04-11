import models
import pprint
import trainer
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
    print 'asin: {}, amaz: {}, avg: {}, smart: {}, error: {}'.format(pro.asin, pro.amazon_rating, pro.average_rating, pro.weighted_rating, pro.amazon_rating - pro.weighted_rating)
  return http.HttpResponse()
