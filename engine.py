import fetcher
import logging
import math
import parser
import scraper
import time
import urllib


def create_product(asin):
  """Creates a Product object for the given ASIN by fetching remote data."""
  page_fetcher = fetcher.PageFetcher()
  # fetch the raw meta data about the product from the Amazon API
  raw_product = page_fetcher.fetch_product(asin)
  if not raw_product:
    logging.info('Failed to fetch product #{} from Amazon.'.format(asin))
    return None
  # create a Product object from the preliminary raw meta data
  product = scraper.get_product(raw_product)
  if not product:
    logging.info('Failed to parse product #{} into object.'.format(asin))
    return None
  # fetch the API review page and extract the first actual review page URL
  base_page = page_fetcher.fetch_pages([product.reviews_url])
  product.reviews_url = scraper.get_reviews_url(base_page)
  # fetch the first review page and extract the review page count and rating
  first_page = page_fetcher.fetch_pages([product.reviews_url])
  page_count = scraper.get_page_count(first_page) or 1
  product.amazon_rating = scraper.get_amazon_rating(first_page)
  # compile a list of all of the review list URLs and fetch simultaneously
  page_urls = [update_url(product.reviews_url, {'page': page})
               for page in range(page_count)]
  review_list_pages = page_fetcher.fetch_pages(page_urls)
  review_list_pages.append(base_page)
  # compile a list of all of the review URLs and fetch simultaneously
  review_urls = []
  for review_list_page in review_list_pages:
    review_urls.extend(scraper.get_review_url_list(review_list_page))
  review_pages = page_fetcher.fetch_pages(review_urls)
  # create Review and Reviewer objects for each review by fetching profiles
  for review_page in review_pages:
    review = scraper.get_review(review_page)
    # create Reviewer objects for each reviewer by fetching their profiles
    reviewer_page = page_fetcher.fetch_profile(review.reviewer_url)
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


def get_weighted_rating(reviews, weights):
  """Computes a weighted rating based on review criteria and weights."""
  minimum = float('inf')
  total = 0
  weighted_rating = 0
  weighted_reviews = []
  # create a list of reviews consisting of the rating and review weight
  for rating, criteria in reviews:
    # sums up the products of each criteria and its weight
    assert len(criteria) == len(weights)
    review_weight = sum([c * w for c, w in zip(criteria, weights)])
    total += review_weight
    minimum = min(minimum, review_weight)
    weighted_reviews.append((rating, review_weight))
  # add up the weighted review ratings to a total weighted rating
  total_votes = total / minimum
  for rating, review_weight in weighted_reviews:
    weighted_rating += rating * (review_weight / minimum / total_votes)
  return weighted_rating


def get_vote_confidence(upvotes, downvotes):
  """Calculates the rank that a pair of upvotes/downvotes has."""
  votes = upvotes + downvotes
  if votes == 0:
    return 0
  confidence = 1.281551565545  # 80% confidence
  positive_ratio = float(upvotes) / votes
  left = positive_ratio + math.pow(confidence, 2) / (2 * votes)
  right = (confidence * math.sqrt(positive_ratio * (1 - positive_ratio) /
           votes + math.pow(confidence, 2) / (4 * math.pow(votes, 2))))
  denominator = 1 + math.pow(confidence, 2) / votes
  return (left - right) / denominator


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
  # compute the sum of the ratings and the total ratings
  total = sum([rating * count for rating, count in rating_distribution])
  count = sum(rating_distribution.itervalues())
  return float(total) / count
