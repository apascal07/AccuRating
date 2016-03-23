from google.appengine.ext import ndb


class Product(ndb.Model):
  """A Product object contains meta data and references to its reviews."""
  # id = ASIN of the product (e.g. B00I5FWWS0)
  # data retrieved from scraping the Amazon pages
  title = ndb.StringProperty(indexed=True, required=True)
  product_url = ndb.StringProperty(indexed=True, required=True)
  reviews_url = ndb.StringProperty(indexed=False, required=True)
  description = ndb.TextProperty(indexed=False)
  reviews = ndb.KeyProperty(indexed=False, kind='Review', repeated=True)
  release_date = ndb.DateTimeProperty(indexed=False, required=True)
  retrieval_date = ndb.DateTimeProperty(indexed=False, required=True,
                                        auto_now_add=True)
  category = ndb.StringProperty(indexed=False, required=True)
  rating_distribution = ndb.PickleProperty(indexed=False, required=True)
  amazon_rating = ndb.FloatProperty(indexed=False, required=True)
  # data computed by the system
  average_rating = ndb.FloatProperty(indexed=False)
  weighted_rating = ndb.FloatProperty(indexed=False)
  standard_deviation = ndb.FloatProperty(indexed=False)


class Review(ndb.Model):
  """A Review object contains a single review for a single product."""
  # id = UID of the review (e.g. R3QE9AHU2XW8IQ)
  # data retrieved from scraping the Amazon pages
  rating = ndb.FloatProperty(indexed=False, required=True)
  text = ndb.TextProperty(indexed=False, required=True)
  reviewer = ndb.KeyProperty(indexed=False, kind='Reviewer', required=True)
  reviewer_url = ndb.StringProperty(indexed=False, required=True)
  upvote_count = ndb.IntegerProperty(indexed=False, required=True)
  downvote_count = ndb.IntegerProperty(indexed=False, required=True)
  verified = ndb.BooleanProperty(indexed=False, required=True)
  timestamp = ndb.DateTimeProperty(indexed=False, required=True)
  # data computed by the system
  text_quality = ndb.FloatProperty(indexed=False)
  weight = ndb.FloatProperty(indexed=True)


class Reviewer(ndb.Model):
  """A Reviewer object contains all of the data associated with a reviewer."""
  # id = UID of the reviewer (e.g. A17HFMUBV1AOGJ)
  # data retrieved from scraping the Amazon pages
  name = ndb.StringProperty(indexed=True, required=True)
  rank = ndb.IntegerProperty(indexed=False, required=True)
  vote_count = ndb.IntegerProperty(indexed=False, required=True)
  rating_distribution = ndb.PickleProperty(indexed=False, required=True)
  creation_date = ndb.DateTimeProperty(indexed=False, required=True)
  # data computed by the system
  average_rating = ndb.FloatProperty(indexed=False)
  standard_deviation = ndb.FloatProperty(indexed=False)
  weight = ndb.FloatProperty(indexed=False)


class TrainingSet(ndb.Model):
  """A TrainingSet object contains meta data about a training attempt."""
  start_timestamp = ndb.DateTimeProperty(indexed=False, auto_now_add=True)
  end_timestamp = ndb.DateTimeProperty(indexed=False)
  criteria = ndb.PickleProperty(indexed=False)
  review_count_limit = ndb.IntegerProperty(indexed=False)
  weights = ndb.PickleProperty(indexed=False)
  product_sample = ndb.KeyProperty(indexed=True, kind='Product', repeated=True)
