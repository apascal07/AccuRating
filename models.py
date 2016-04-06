import common
import datetime
import fetcher
import logging
import math
import parser
import scraper
from google.appengine.ext import ndb


PRODUCT_REVIEWS_URL = 'http://amazon.com/product-reviews/{asin}'


class Product(ndb.Model):
  """A Product object contains meta data and references to its reviews."""

  # Data retrieved from scraping the Amazon pages.
  title = ndb.StringProperty(indexed=True, required=True)
  product_url = ndb.StringProperty(indexed=False, required=True)
  description = ndb.TextProperty(indexed=False)
  reviews = ndb.KeyProperty(indexed=False, kind='Review', repeated=True)
  retrieval_timestamp = ndb.DateTimeProperty(indexed=False, auto_now_add=True)
  newest_timestamp = ndb.DateTimeProperty(indexed=False)
  oldest_timestamp = ndb.DateTimeProperty(indexed=False)
  amazon_rating = ndb.FloatProperty(indexed=False)

  # Data computed by the system.
  average_rating = ndb.FloatProperty(indexed=False)
  weighted_rating = ndb.FloatProperty(indexed=False)
  training_set = ndb.KeyProperty(indexed=False, kind='TrainingSet')

  @classmethod
  @common.timer
  def create_product(self, asin, force=False):
    """Creates a Product object for the given ASIN by fetching remote data."""
    page_fetcher = fetcher.PageFetcher()
    # Fetch product metadata from the Amazon API and create a Product object.
    product_meta = page_fetcher.fetch_product(asin)
    product = scraper.get_product(product_meta)
    # Fetch the summary review page and extract the first review list page URL.
    #base_page = page_fetcher.fetch_pages([product.reviews_url])[0]
    #product.reviews_url = scraper.get_reviews_url(base_page)
    # Fetch the first review list page and extract the page count and rating.
    product_reviews_url = PRODUCT_REVIEWS_URL.format(asin=asin)
    first_page = page_fetcher.fetch_pages([product_reviews_url])[0]
    page_count = scraper.get_page_count(first_page) or 1
    product.amazon_rating = scraper.get_amazon_rating(first_page)
    # Compile a list of review list page URLs and fetch all review list pages.
    review_list_urls = [common.update_url(product.reviews_url, {'page': page})
                        for page in range(page_count)]
    review_list_pages = page_fetcher.fetch_pages(review_list_urls)
    review_list_pages.append(first_page)
    # Compile a list of all of the review page URLs and fetch all review pages.
    review_page_urls = []
    for review_list_page in review_list_pages:
      review_page_urls.extend(scraper.get_review_url_list(review_list_page))
    review_pages = page_fetcher.fetch_pages(review_page_urls)
    # Create Review objects, update oldest/newest review date, and save.
    product.oldest_date = datetime.datetime.now()
    product.newest_date = datetime.datetime(1970, 1, 1)
    for review_page in review_pages:
      review = scraper.get_review(review_page)
      product.oldest_date = min(product.oldest_date, review.timestamp)
      product.newest_date = max(product.newest_date, review.timestamp)
      reviewer_page = page_fetcher.fetch_pages([review.reviewer_url])[0]
      review.reviewer_rank = scraper.get_rank(reviewer_page)
      review.put()
      product.reviews.append(review.key)
    # Process the Product to compute all dynamic criteria values.
    product.set_dynamic_criteria()
    # Set the weighted rating if a TrainingSet is available.
    product.set_weighted_rating()
    product.put()
    return product

  @common.timer
  def set_dynamic_criteria(self):
    """Generates and sets all dynamic criteria values."""
    reviews = Review.get_all_by_ids(self.reviews)
    text_parser = parser.Parser(reviews, self.description)
    total = 0.0
    for review in reviews:
      review.set_dynamic_criteria(text_parser, self.oldest_timestamp,
                                  self.newest_timestamp)
      total += review.rating
    self.average_rating = total / len(reviews)
    self.put()

  def set_weighted_rating(self, training_set=None):
    """Computes and sets the weighted rating if it was successful."""
    weighted_rating = self.get_weighted_rating(None, training_set)
    if weighted_rating:
      self.weighted_rating = weighted_rating
      self.training_set = training_set
      self.training_set.put()
      self.put()
      return True
    return False

  def get_weighted_rating(self, reviews=None, training_set=None):
    """Computes a weighted rating based on review criteria and weights."""
    # Fetch the associated Review objects and latest TrainingSet object.
    reviews = reviews or Review.get_all_by_ids(self.reviews)
    training_set = (training_set or self.training_set or
                    TrainingSet.get_latest_set())
    # Unable to get a weighted rating if there are no weights.
    if not training_set:
      return None
    # Sum up the products of each criteria and its weight.
    total = 0.0
    for review in reviews:
      review.weight = sum([getattr(review, c, 0) * w for c, w in
                           training_set.criteria_weights.iteritems()])
      total += review.weight
    # Add up the weighted review ratings to a total weighted rating.
    weighted_rating = sum([review.rating * review.weight / total
                           for review in reviews])
    return weighted_rating


class Review(ndb.Model):
  """A Review object contains a single review for a single product."""

  # Data retrieved from scraping the Amazon pages.
  rating = ndb.FloatProperty(indexed=False, required=True)
  text = ndb.TextProperty(indexed=False, required=True)
  upvote_count = ndb.IntegerProperty(indexed=False, default=0)
  downvote_count = ndb.IntegerProperty(indexed=False, default=0)
  timestamp = ndb.DateTimeProperty(indexed=False, required=True)
  reviewer_url = ndb.StringProperty(indexed=False, required=True)
  reviewer_name = ndb.StringProperty(indexed=False, required=False)  # FIX!
  reviewer_rank = ndb.IntegerProperty(indexed=False, default=0)

  # Available dynamic criteria generated by the system.
  verified = ndb.FloatProperty(indexed=False, default=0)
  review_age = ndb.FloatProperty(indexed=False, default=0)
  vote_confidence = ndb.FloatProperty(indexed=False, default=0)
  text_quality = ndb.FloatProperty(indexed=False, default=0)
  relative_rank = ndb.FloatProperty(indexed=False, default=0)

  # Data generated by the system.
  weight = ndb.FloatProperty(indexed=True, default=0)

  @common.timer
  def set_dynamic_criteria(self, text_parser, oldest, newest):
    """Generates and sets all dynamic criteria values."""
    self.vote_confidence = self.get_vote_confidence(
        self.upvote_count, self.downvote_count)
    self.text_quality = text_parser.get_text_quality(self.text)
    self.review_age = self.get_review_age(oldest, newest, self.timestamp)
    self.relative_rank = self.get_relative_rank(self.reviewer_rank)
    self.put()

  @classmethod
  def get_all_by_ids(self, ids):
    """Retrives all of the Review objects for the list of ids."""
    return self.query().filter(Review.key.IN(ids)).fetch()

  @staticmethod
  def get_vote_confidence(upvotes, downvotes):
    """Calculates the vote confidence based on the upvote/downvote count."""
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

  @staticmethod
  def get_review_age(oldest, newest, this):
    """Calculates the relative review age in the window of oldest to newest."""
    delta = (this - oldest).total_seconds()
    window = (newest - oldest).total_seconds()
    return float(delta) / window

  @staticmethod
  def get_relative_rank(rank):
    """Calculates the relative rank based on an integer rank from 1-1000000."""
    return min(max(0.5 + 0.7 * math.atan(float(-rank) / 250000 + 2) /
                   (math.pi / 2), 0), 1) if rank > 0 else 0


class TrainingSet(ndb.Model):
  """A TrainingSet object contains meta data about a training attempt."""
  start_timestamp = ndb.DateTimeProperty(indexed=False, auto_now_add=True)
  end_timestamp = ndb.DateTimeProperty(indexed=True)
  criteria_weights = ndb.PickleProperty(indexed=False)
  review_count_limit = ndb.IntegerProperty(indexed=False)
  product_sample = ndb.KeyProperty(indexed=True, kind='Product')

  @classmethod
  def get_latest_set(self):
    return self.query().order(-TrainingSet.end_timestamp).get()
