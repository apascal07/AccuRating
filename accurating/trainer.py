import abstract
import common
import copy
import datetime
import models


CRITERIA = ('verified', 'review_age', 'vote_confidence', 'relative_rank')


class Trainer(abstract.AbstractTrainer):

  @common.timer
  def train(self, asins, criteria=None, increments=20):
    """Trains the weighted rating weights using the given sample products."""
    criteria = criteria or CRITERIA

    # Retrieve all sample products, reviews, and the baseline target delta.
    products = [models.Product.get_or_create_product(asin) for asin in asins]
    training_set = models.TrainingSet()
    training_set.criteria_weights = {criterion: 0 for criterion in criteria}
    reviews = [product.reviews.all() for product in products]
    min_delta = sum([abs(product.amazon_rating - product.average_rating) for
                     product in products])
    min_delta_weights = training_set.criteria_weights

    # Generate the criteria weights matrix and try each permutation.
    training_set.start_timestamp = datetime.datetime.now()
    weights_matrix = Trainer.multichoose(len(criteria), increments)
    for weights_vector in weights_matrix:

      # Unpacks the criteria weights from JSON form, updates, and repacks.
      criteria_weights = training_set.criteria_weights
      for criterion, weight in zip(criteria, weights_vector):
        criteria_weights[criterion] = float(weight) / increments
        training_set.criteria_weights = criteria_weights

      # Calculate the weighted ratings and find the sum of the target deltas.
      weighted_ratings = [product.get_weighted_rating(reviews[i], training_set)
                          for i, product in enumerate(products)]
      delta = sum([abs(product.amazon_rating - weighted_rating) for product,
                   weighted_rating in zip(products, weighted_ratings)])
      if delta < min_delta:
        min_delta = delta
        min_delta_weights = copy.deepcopy(training_set.criteria_weights)

    # Set the weighted rating for each product using the optimal weights set.
    training_set.end_timestamp = datetime.datetime.now()
    training_set.criteria_weights = min_delta_weights
    training_set.save()
    training_set.training_products.add(*products)
    training_set.save()

    return training_set

  @staticmethod
  def multichoose(n, k):
    """Generates a list N multichoose K steps."""
    if not k:
      return [[0] * n]
    if not n:
      return []
    if n == 1:
      return [[k]]
    return ([[0] + val for val in Trainer.multichoose(n - 1, k)] + [[val[0] +
            1] + val[1:] for val in Trainer.multichoose(n, k - 1)])
