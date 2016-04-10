import logging
import models


def get_product(asin):
  """Retrieves a Product object for the given ASIN."""
  logging.info('Retrieving product #{} from datastore...'.format(asin))
  product = models.Product.get_by_asin(asin)
  # TODO: invalidate a product after a certain time delta (24-48 hours)
  if not product:
    logging.info('Product #{} not in datastore. Creating...'.format(asin))
    product = models.Product.create_product(asin)
  return product


def get_top_reviews(product_id):
  """Retrieves a list of top Review objects for a given product ID."""
  pass


def get_reviews(review_ids):
  """Retrieves a list of Review objects for a given list of review IDs."""
  pass
