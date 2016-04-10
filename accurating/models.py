import common
import datetime
import fetcher
import json
import math
import parser
import pprint
import re
import scraper

from django.db import models


REVIEW_LIST_URL = 'http://amazon.com/product-reviews/{asin}/'
REVIEW_PAGE_URL = 'http://amazon.com/review/{uid}/'
MAX_RETRIES = 10


class Product(models.Model):
  """A Product object contains meta data and references to its reviews."""

  # Data retrieved from scraping the Amazon pages.
  asin = models.CharField(max_length=32)
  title = models.CharField(max_length=300)
  product_url = models.URLField()
  description = models.TextField()
  reviews = models.ManyToManyField('Review')
  retrieved = models.DateTimeField(auto_now_add=True)
  newest = models.DateTimeField(null=True, blank=True, default=None)
  oldest = models.DateTimeField(null=True, blank=True, default=None)
  amazon_rating = models.FloatField()

  # Data computed by the system.
  average_rating = models.FloatField(null=True, blank=True, default=None)
  weighted_rating = models.FloatField(null=True, blank=True, default=None)
  training_set = models.ForeignKey('TrainingSet', models.SET_NULL, null=True)

  @classmethod
  @common.timer
  def get_or_create_product(self, asin):
    """Retrieves the product, if it exists, else creates from remote data."""
    product = self.get_product(asin)
    if not product:
      print 'Beginning fetching process for product #{}...'.format(asin)
      product = self.create_product(asin)
    return product

  @classmethod
  @common.timer
  def get_product(self, asin):
    """Retrieves the product from the database."""
    product = None
    try:
      product = self.objects.get(asin=asin)
    except self.DoesNotExist:
      print 'Product #{} does not exist in the database.'.format(asin)
    return product

  @classmethod
  @common.timer
  def create_product(self, asin):
    """Creates a product for the given ASIN by fetching remote data."""
    page_fetcher = fetcher.PageFetcher()

    # Fetch product metadata from the Amazon API and create a Product object.
    print 'Fetching product #{} from Amazon API...'.format(asin)
    product_meta = page_fetcher.fetch_product(asin)
    product = scraper.get_product(product_meta)

    # Fetch the first review list page and extract the page count and rating.
    reviews_url = REVIEW_LIST_URL.format(asin=asin)
    print 'Fetching first page of reviews...'
    first_page = page_fetcher.fetch_page(reviews_url)
    page_count = scraper.get_page_count(first_page) or 1
    print 'Found {} pages of reviews...'.format(page_count)
    product.amazon_rating = scraper.get_amazon_rating(first_page)

    # Compile a list of review list page URLs and fetch all review list pages.
    review_list_pages = [first_page]
    for i in range(2, page_count + 1):
      paginated_url = common.update_url(reviews_url, {'pageNumber': i})
      print 'Fetching page {} of reviews...'.format(i)
      review_list_page = page_fetcher.fetch_page(paginated_url)
      review_list_pages.append(review_list_page)

    # Fetch each review and its associated reviewer and populate the database.
    reviews = []
    product.oldest = datetime.datetime.now()
    product.newest = datetime.datetime(1970, 1, 1)
    for i, review_list_page in enumerate(review_list_pages):
      print 'Scraping page {} of reviews...'.format(i + 1)
      review_page_urls = scraper.get_review_url_list(review_list_page)
      for review_page_url in review_page_urls:
        review_uid = Review.get_uid_from_url(review_page_url)
        review = Review.get_or_create_review(review_uid, page_fetcher)
        product.oldest = min(product.oldest, review.timestamp)
        product.newest = max(product.newest, review.timestamp)
        reviews.append(review)

    # Save the product to init the object and add the now-successful reviews.
    product.save()
    product.reviews.add(*reviews)

    # Process the product's dynamic criteria and possibly weighted rating.
    product.set_dynamic_criteria()
    product.set_weighted_rating()
    product.save()

    # Close the browser instance used to fetch pages.
    page_fetcher.driver.close()

    return product

  @common.timer
  def set_dynamic_criteria(self):
    """Generates and sets all dynamic criteria values."""
    reviews = self.reviews.all()
    text_parser = parser.TextParser(reviews, self.description)
    total = 0.0
    for review in reviews:
      review.set_dynamic_criteria(text_parser, self.oldest, self.newest)
      total += review.rating
    self.average_rating = total / len(reviews)
    self.save()

  def set_weighted_rating(self, training_set=None):
    """Computes and sets the weighted rating if it was successful."""
    try:
      training_set = (training_set or self.training_set or
                      TrainingSet.objects.latest())
    except TrainingSet.DoesNotExist:
      training_set = None
    if not training_set:
      return False
    weighted_rating = self.get_weighted_rating(None, training_set)
    if weighted_rating:
      self.weighted_rating = weighted_rating
      self.training_set = training_set
      self.training_set.save()
      self.save()
      return True
    return False

  def get_weighted_rating(self, reviews=None, training_set=None):
    """Computes a weighted rating based on review criteria and weights."""
    # Fetch the associated Review objects and latest TrainingSet object.
    reviews = reviews or self.reviews.all()
    # Sum up the products of each criteria and its weight.
    total = 0.0
    for review in reviews:
      review.weight = sum([getattr(review, c, 0) * w for c, w in
                           training_set.criteria_weights.iteritems()])
      total += review.weight
    # Add up the weighted review ratings to a total weighted rating.
    weighted_rating = sum([review.rating * review.weight / total
                           for review in reviews]) if total else 0
    return weighted_rating


class Review(models.Model):
  """A Review object contains a single review for a single product."""

  # Data retrieved from scraping the Amazon pages.
  uid = models.CharField(max_length=16)
  rating = models.FloatField()
  text = models.TextField()
  upvote_count = models.IntegerField(default=0)
  downvote_count = models.IntegerField(default=0)
  timestamp = models.DateTimeField()
  reviewer_url = models.URLField()
  reviewer_name = models.CharField(max_length=64)
  reviewer_rank = models.IntegerField(default=0)

  # Available dynamic criteria generated by the system.
  verified = models.FloatField(default=0.0)
  review_age = models.FloatField(default=0.0)
  vote_confidence = models.FloatField(default=0.0)
  text_quality = models.FloatField(default=0.0)
  relative_rank = models.FloatField(default=0.0)

  # Data generated by the system.
  weight = models.FloatField(default=0.0)

  @classmethod
  @common.timer
  def get_or_create_review(self, uid, page_fetcher=None):
    """Retrieves the review, if it exists, else creates from remote data."""
    review = self.get_review(uid)
    if not review:
      print 'Beginning fetching process for review #{}...'.format(uid)
      review = self.create_review(uid, page_fetcher)
    return review

  @classmethod
  @common.timer
  def get_review(self, uid):
    """Retrieves the review from the database."""
    review = None
    try:
      review = self.objects.get(uid=uid)
      print 'Retrieved review #{} from the database.'.format(uid)
    except self.DoesNotExist:
      print 'Review #{} does not exist in the database.'.format(uid)
    return review

  @classmethod
  @common.timer
  def create_review(self, uid, page_fetcher=None):
    """Creates a review for the given UID by fetching remote data."""
    page_fetcher = page_fetcher or fetcher.PageFetcher()
    review_page_url = REVIEW_PAGE_URL.format(uid=uid)
    retries = 0
    for _ in range(MAX_RETRIES):
      retries += 1
      review_page = page_fetcher.fetch_page(review_page_url)
      try:
        review = scraper.get_review(review_page)
        break
      except Exception:
        print 'Attempt {} to parse review URL {} failed.'.format(
            retries, review_page_url)
    reviewer_page = page_fetcher.fetch_page(review.reviewer_url)
    review.reviewer_rank = scraper.get_rank(reviewer_page)
    review.uid = uid
    review.save()
    print 'Review #{} has been fetched, created, and saved.'.format(uid)
    return review

  @common.timer
  def set_dynamic_criteria(self, text_parser, oldest, newest):
    """Generates and sets all dynamic criteria values."""
    self.vote_confidence = self.get_vote_confidence(
        self.upvote_count, self.downvote_count)
    self.text_quality = text_parser.get_text_quality(self.text)
    self.review_age = self.get_review_age(oldest, newest, self.timestamp)
    self.relative_rank = self.get_relative_rank(self.reviewer_rank)
    self.save()

  @classmethod
  def get_all_by_ids(self, ids):
    """Retrives all of the Review objects for the list of ids."""
    return self.objects.filter(id__in=ids)

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

  @staticmethod
  def get_uid_from_url(url):
    """Extracts the review UID from a given URL."""
    match = re.search(r'review[s]?\/([a-zA-Z0-9]*)\/?', url)
    return match.group(1) if match else None


class TrainingSet(models.Model):
  """A TrainingSet object contains meta data about a training attempt."""
  start_timestamp = models.DateTimeField(auto_now_add=True)
  end_timestamp = models.DateTimeField()
  _criteria_weights = models.TextField(null=True)
  training_product = models.ForeignKey('Product', models.CASCADE)

  @property
  def criteria_weights(self):
    return json.loads(self._criteria_weights)

  @criteria_weights.setter
  def criteria_weights(self, criteria_weights):
    self._criteria_weights = json.dumps(criteria_weights)

  class Meta:
    get_latest_by = 'end_timestamp'
