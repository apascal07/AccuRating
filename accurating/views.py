import models
import pprint
import trainer
import verifier
from django import http, shortcuts


def search_view(request, **kwargs):
  if 'asin' in request.GET:
    return shortcuts.redirect(results_view, asin=request.GET.get('asin'))
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
  if request.method == 'POST':
    op_type = request.POST.get('op-type')
    if op_type == 'train':
      asins = set(request.POST.getlist('asin', []))
      new_asins = request.POST.get('new-asin', '')
      new_asins = filter(None, [a.strip() for a in new_asins.split(',')])
      asins.update(new_asins)
      weight_trainer = trainer.Trainer()
      training_set = weight_trainer.train(asins)
      pprint.pprint(training_set.__dict__)
    elif op_type == 'delete':
      uid = request.POST.get('uid')
      training_set = models.TrainingSet.objects.get(id=uid)
      if training_set.active:
        new_set = models.TrainingSet.objects.latest('end_timestamp')
        new_set.active = True
        new_set.save()
      training_set.delete()
    elif op_type == 'set_active':
      uid = request.POST.get('uid')
      training_set = models.TrainingSet.objects.get(id=uid)
      try:
        old_set = models.TrainingSet.objects.get(active=True)
        old_set.active = False
        old_set.save()
      except models.TrainingSet.DoesNotExist:
        pass
      training_set.active = True
      training_set.save()
      for product in models.Product.objects.all():
        product.set_weighted_rating()
  context = {
      'view_template': 'train.html',
      'products': models.Product.objects.all(),
      'training_sets': (models.TrainingSet.objects.order_by('-active', '-end_timestamp').all())
  }
  return shortcuts.render(request, 'base.html', context)


def verification_handler(request):
  asins = [p.asin for p in models.Product.objects.all()]
  return http.HttpResponse(str(verifier.verify(asins)))
