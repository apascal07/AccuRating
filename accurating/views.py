import models
import pprint
import trainer
import verifier
from django import http, shortcuts


def search_view(request, **kwargs):
  context = {
      'view_template': 'search.html',
      'products': models.Product.objects.all()
  }
  return shortcuts.render(request, 'base.html', context)


def results_view(request, **kwargs):
  asin = kwargs.get('asin')
  product = models.Product.get_or_create_product(asin)
  reviews = product.reviews.order_by('-weight').all()
  context = {
      'view_template': 'results.html',
      'product': product,
      'reviews': reviews
  }
  return shortcuts.render(request, 'base.html', context)


def training_view(request, **kwargs):
  context = {
      'view_template': 'dashboard.html'
  }
  trainer_ = trainer.Trainer()
  ps = [p.asin for p in models.Product.objects.all()]
  tset = trainer_.train(ps)
  pprint.pprint(tset.__dict__)
  for p in ps:
    pro = models.Product.get_product(p)
    print 'asin: {}, amaz: {}, avg: {}, smart: {}, error: {}'.format(pro.asin, pro.amazon_rating, pro.average_rating, pro.weighted_rating, pro.amazon_rating - pro.weighted_rating)
  return shortcuts.render(request, 'base.html', context)
