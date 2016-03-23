import fetcher
import logging
import models
import scraper
from google.appengine.ext import ndb


def create_product(asin):
  """Creates a Product object for the given ASIN by fetching remote data."""
  # fetch the raw meta data about the product from the Amazon API
  raw_product = fetcher.fetch_product(asin)
  if not raw_product:
    logging.info('Failed to fetch product #{} from Amazon.'.format(asin))
    return None
  # create a Product object from the preliminary raw meta data
  product = scraper.get_product(raw_product)
  if not product:
    logging.info('Failed to parse product #{} from Amazon.'.format(asin))
    return None
  # fetch the base review page and find the number of total review pages
  base_url = product.reviews_url
  base_page = [fetcher.get_pages([base_url])]
  page_count = scraper.get_page_count(base_page) or 1
  # compile a list of all of the review page URLs and fetch simultaneously
  page_urls = [get_url(base_url, page) for page in range(page_count)]
  review_pages = fetcher.get_pages(page_urls)
  review_pages.append(base_page)
  # create Review objects for each review and compile list of reviewer URLs
  for review_page in review_pages:
    reviews = scraper.get_reviews(review_page)
    # create Reviewer objects for each reviewer by fetching their profiles
    for review in reviews:
      reviewer_page = fetcher.get_profile(review.reviewer_url)
      reviewer = scraper.get_profile(reviewer_page)
      # calculate the Reviewer's average rating and standard deviation
      reviewer.average_rating = get_average(reviewer.rating_distribution)
      reviewer.standard_deviation = get_deviation(reviewer.rating_distribution)
      reviewer.put()
      # associate the Reviewer with the Review and write to datastore
      review.reviewer = reviewer
      review.put()
    # append the new Review objects to the Product object
    product.reviews.extend(reviews)
  product.put()
  return product



def get_url(base_url, page):
  pass


def get_deviation(a):
  pass


def get_average(rating_distribution):
  """Computes the average rating based on a distribution ranging from 1-5."""
  if not rating_distribution:
    logging.warning('Rating distribution is empty.')
    return None
  if len(rating_distribution) < 5:
    logging.warning('Rating distribution has fewer than 5 star buckets.')
  total = sum([rating * count for rating, count in rating_distribution])
  count = sum(rating_distribution.itervalues())
  return float(total) / count
