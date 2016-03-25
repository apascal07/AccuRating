import fetcher
import logging
import math
import parser
import scraper
import time
import urllib


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
  url = product.reviews_url
  base_page = fetcher.fetch_pages([url])
  page_count = scraper.get_page_count(base_page) or 1
  # compile a list of all of the review list URLs and fetch simultaneously
  page_urls = [update_url(url, {'page': page}) for page in range(page_count)]
  review_list_pages = fetcher.fetch_pages(page_urls)
  review_list_pages.append(base_page)
  # compile a list of all of the review URLs and fetch simultaneously
  review_urls = []
  for review_list_page in review_list_pages:
    review_urls.extend(scraper.get_review_urls(review_list_page))
  review_pages = fetcher.fetch_pages(review_urls)
  # create Review and Reviewer objects for each review by fetching profiles
  for review_page in review_pages:
    review = scraper.get_review(review_page)
    # create Reviewer objects for each reviewer by fetching their profiles
    reviewer_page = fetcher.fetch_profile(review.reviewer_url)
    reviewer = scraper.get_profile(reviewer_page)
    # calculate the Reviewer's average rating and standard deviation
    reviewer.average_rating = get_average(reviewer.rating_distribution)
    # reviewer.standard_deviation = get_deviation(reviewer.rating_distribution)
    reviewer.put()
    # assess the quality of the review text and set the Reviewer object
    review.text_quality = parser.get_value(review.text)
    review.reviewer = reviewer.key
    review.put()
    # append the new Review object to the Product object
    product.reviews.append(review.key)
  product.put()
  return product


def process_product(product):
  pass


def weigh_product(product, weights=None):
  pass


def get_vote_confidence(upvotes, downvotes):
  """Calculates the rank that a pair of upvotes/downvotes has."""
  # source: https://medium.com/hacking-and-gonzo/how-reddit-ranking-algorithms-
  #     work-ef111e33d0d9#.krp5goqqb
  n = upvotes + downvotes
  if n == 0:
    return 0
  z = 1.281551565545  # 80% confidence
  p = float(upvotes) / n
  l = p + math.pow(z, 2) / (2 * n)
  r = z * math.sqrt(p * (1 - p) / n + math.pow(z, 2) / (4 * math.pow(n, 2)))
  d = 1 + math.pow(z, 2) / n
  return (l - r) / d


def timer(fn):
  """Clocks the time it takes a function to execute."""
  def wrapper(*args, **kwargs):
    start = time.time()
    result = fn(*args, **kwargs)
    end = time.time()
    delta = end - start
    logging.info('Executed {} in {} sec(s).'.format(fn.__name__, delta))
    return result
  return wrapper


def update_url(url, new_params):
  """Updates the given URL to include (add/replace) the given parameters."""
  if not new_params:
    return url
  # extract any existing parameters in the URL
  url = urllib.unquote(url)
  parsed_url = urllib.urlparse(url)
  params = dict(urllib.parse_qsl(parsed_url.query))
  # update the parameter dictionary with the new parameters
  params.update(new_params)
  # encode the parameter query string and recreate the full URL again
  query = urllib.urlencode(params)
  base_url = url.split('?')[0]
  new_url = '{}?{}'.format(base_url, query)
  return new_url


def get_average(rating_distribution):
  """Computes the average rating based on a distribution ranging from 1-5."""
  if not rating_distribution:
    logging.info('Rating distribution is empty.')
    return 0
  if len(rating_distribution) < 5:
    logging.info('Rating distribution has fewer than 5 star buckets.')
  total = sum([rating * count for rating, count in rating_distribution])
  count = sum(rating_distribution.itervalues())
  return float(total) / count
