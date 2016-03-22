from google.appengine.ext import ndb

class Review(ndb.Model):
  """A Review object contains a single review for a single product."""
  rating = ndb.FloatProperty(indexed=False)
  text = ndb.TextProperty(indexed=False)
  text_quality = ndb.FloatProperty(indexed=False)
  reviewer = ndb.KeyProperty(key='Reviewer', indexed=False)
  product = ndb.KeyProperty(key='Product', indexed=False)
  good_vote_count = ndb.IntegerProperty(indexed=False)
  total_vote_count = ndb.IntegerProperty(indexed=False)
  verified = ndb.BooleanProperty(indexed=False)
  timestamp = ndb.DateTimeProperty(indexed=False, auto_now_add=False)
  weight = ndb.FloatProperty(indexed=False)

class Reviewer(ndb.Model):
  """A Reviewer object contains all of the data associated with a reviewer."""
  name = ndb.StringProperty(indexed=True)
  rank = ndb.IntegerProperty(indexed=False)
  vote_count = ndb.IntegerProperty(indexed=False)
  reviews = ndb.KeyProperty(key='Review', repeated=True)
  creation_date = ndb.DateTimeProperty(indexed=False)
  average_rating = ndb.FloatProperty(indexed=False)
  standard_deviation = ndb.FloatProperty(indexed=False)
  weight = ndb.FloatProperty(indexed=False)

class Product(ndb.Model):
  """A Product object contains meta data and references to its reviews."""
  title = ndb.StringProperty(indexed=False)
  description = ndb.TextProperty(indexed=False)
  reviews = ndb.KeyProperty(key='Review', repeated=True)
  amazon_rating = ndb.FloatProperty(indexed=False)
  simple_rating = ndb.FloatProperty(indexed=False)
  weighted_rating = ndb.FloatProperty(indexed=False)
  category = ndb.StringProperty(indexed=False)
  release_date = ndb.DateTimeProperty(indexed=False, auto_now_add=False)

class TrainingSet(ndb.Model):
  """A TrainingSet object contains meta data about a training attempt."""
  pass
