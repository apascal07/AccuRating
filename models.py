import enum
from google.appengine.ext import ndb

class Review(ndb.Model):
  """A Review object contains a single review for a single product."""
  # data retrieved from scraping the Amazon pages
  rating = ndb.FloatProperty(indexed=False, required=True)
  text = ndb.TextProperty(indexed=False, required=True)
  reviewer = ndb.KeyProperty(indexed=False, key='Reviewer', required=True)
  product = ndb.KeyProperty(indexed=False, key='Product', required=True)
  good_vote_count = ndb.IntegerProperty(indexed=False, required=True)
  total_vote_count = ndb.IntegerProperty(indexed=False, required=True)
  verified = ndb.BooleanProperty(indexed=False, required=True)
  timestamp = ndb.DateTimeProperty(indexed=False, required=True)
  # data computed by the system
  text_quality = ndb.FloatProperty(indexed=False)
  weight = ndb.FloatProperty(indexed=False)

class Reviewer(ndb.Model):
  """A Reviewer object contains all of the data associated with a reviewer."""
  # data retrieved from scraping the Amazon pages
  name = ndb.StringProperty(indexed=True, required=True)
  rank = ndb.IntegerProperty(indexed=False, required=True)
  vote_count = ndb.IntegerProperty(indexed=False, required=True)
  reviews = ndb.KeyProperty(indexed=False, key='Review', repeated=True)
  # data computed by the system
  creation_date = ndb.DateTimeProperty(indexed=False)
  average_rating = ndb.FloatProperty(indexed=False)
  standard_deviation = ndb.FloatProperty(indexed=False)
  weight = ndb.FloatProperty(indexed=False)

class Product(ndb.Model):
  """A Product object contains meta data and references to its reviews."""
  # data retrieved from scraping the Amazon pages
  title = ndb.StringProperty(indexed=True, required=True)
  description = ndb.TextProperty(indexed=False)
  reviews = ndb.KeyProperty(indexed=False, key='Review', repeated=True)
  release_date = ndb.DateTimeProperty(indexed=False, required=True)
  category = ndb.StringProperty(indexed=False, required=True)
  rating_distribution = ndb.PickleProperty(indexed=False, required=True)
  amazon_rating = ndb.FloatProperty(indexed=False, required=True)
  # data computed by the system
  average_rating = ndb.FloatProperty(indexed=False)
  weighted_rating = ndb.FloatProperty(indexed=False)

class TrainingSet(ndb.Model):
  """A TrainingSet object contains meta data about a training attempt."""
  start_timestamp = ndb.DateTimeProperty(indexed=False, auto_now_add=True)
  end_timestamp = ndb.DateTimeProperty(indexed=False)
  criteria = ndb.PickleProperty(indexed=False)
  review_count_limit = ndb.IntegerProperty(indexed=False)
  weights = ndb.PickleProperty(indexed=False)
  product_sample = ndb.KeyProperty(indexed=True, key='Product',
      repeated=True)
  status = ndb.PickleProperty(indexed=False, default=Status.idle)

class Status(enum.Enum):
  """Enumerates the states that a TrainingSet can be in."""
  idle = 0
  running = 1
  interrupted = 2
  finished = 3
