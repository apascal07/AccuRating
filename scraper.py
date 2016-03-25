"""Scraper extracts data from raw HTML and creates corresponding objects."""
import models
import bs4
import datetime


def get_page_count(html):
  pass


def get_review_urls(html):
  pass


def get_review(html):
  pass


def get_profile(html):
  pass


def get_product(html):
  product = models.Product()
  soup = bs4.BeautifulSoup(html, "html.parser")
  xml = soup.itemlookupresponse.items.item

  product.title = xml.itemattributes.title.string
  product.product_url = xml.detailpageurl.string
  product.reviews_url = xml.customerreviews.iframeurl.string
  product.retrieval_date = datetime.datetime.today()
  product.category = xml.itemattributes.productgroup.string
  # product.reviews = None
  # product.release_date = None
  # product.rating_distribution = None
  # product.amazon_rating = None

  # concatenate all description data
  features = xml.itemattributes.find_all('feature')
  product.description = '. '.join([feature.string for feature in features]) + '. '
  for editorial_review in xml.editorialreviews.find_all('editorialreview'):
    if editorial_review.source.string == 'Product Description':
      product.description += editorial_review.content.string

  return product
