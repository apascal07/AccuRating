"""Trainer trains a set of criteria weights based on sample training data."""
import common
import datetime
import models


@common.timer
def train(asin):
  criteria = ['verified', 'review_age', 'vote_confidence', 'text_quality', 'relative_rank']
  n_steps = 20

  product = models.Product.get_or_create_product(asin)
  training_set = models.TrainingSet()
  training_set.training_product = product
  reviews = product.reviews.all()
  amazon_rating = product.amazon_rating
  min_error = abs(amazon_rating - product.average_rating)
  min_error_weights = None

  steps_list = _multichoose(len(criteria), n_steps)
  for steps in steps_list:
    training_set.criteria_weights = {criteria[i]: float(steps[i]) / n_steps for i in xrange(len(criteria))}
    print training_set.criteria_weights
    weighted_rating = product.get_weighted_rating(reviews, training_set)
    local_error = abs(amazon_rating - weighted_rating)
    if local_error < min_error:
      min_error = local_error
      min_error_weights = training_set.criteria_weights
  training_set.end_timestamp = datetime.datetime.now()
  if min_error_weights:
    training_set.criteria_weights = min_error_weights
    product.set_weighted_rating(training_set)
  training_set.save()
  return training_set


def get_progress():
  pass


def _multichoose(n, k):
  """n is num weights and k is the num steps"""
  if k < 0 or n < 0: return "Error"
  if not k: return [[0] * n]
  if not n: return []
  if n == 1: return [[k]]
  return [[0]+val for val in _multichoose(n-1, k)] + [[val[0]+1]+val[1:] for val in _multichoose(n,k-1)]
