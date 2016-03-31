"""Scraper extracts data from raw HTML and creates corresponding objects."""
import models
import bs4
import datetime
import re

num_format = '(\d+|\d{1,3}(,\d{3})*)(\.\d+)?$'

def _get_date(date_str):
  """
  Attempts to parse a valid time using Amazon's format
  :param time_str: a string to parse
  :return: A valid datetime, or None if the conversion was invalid
  """
  re.sub(' (\d) ', ' 0{} ', date_str)
  try:
    return datetime.datetime.strptime(date_str, '%B %d, %Y')
  except ValueError:
    return None


def get_reviews_url(html):
  dom = bs4.BeautifulSoup(html, 'html.parser')
  return dom.select('.crIframeReviewList span.small > b > a')[0]['href']


def get_amazon_rating(html):
  dom = bs4.BeautifulSoup(html, 'html.parser')
  return float(dom.select('.arp-rating-out-of-text').pop().text[:3])


def get_page_count(html):
  dom = bs4.BeautifulSoup(html, 'html.parser')
  return int(dom.select('.page-button').pop().text)


def get_review_url_list(html):
  dom = bs4.BeautifulSoup(html, 'html.parser')
  titles = dom.select('a.review-title')
  return ['http://www.amazon.com{}'.format(title['href']) for title in titles]


def get_review(html):
  """
  Parses a review object based on an html string
  :param html: A string containing the html of a reviewer page
  :return: A parsed reviewer object
  """
  review = models.Review()
  dom = bs4.BeautifulSoup(html, 'html.parser')

  # parse the 'hReview' element that contains several needed pieces of data
  review.text = dom.select('.hReview .description')[0].text
  review.verified = len(dom.select('.verifyWhatsThis')) > 0
  review.timestamp = filter(None, [_get_date(tag.text) for tag in dom.select('nobr')])[0]

  reviewer_element = dom.select('.hReview .reviewer .url')[0]
  review.reviewer_url = 'http://www.amazon.com'.format(reviewer_element['href'])

  vote_text = dom.find(text=re.compile(num_format + ' of ' + num_format +
                                        ' people found the following review helpful'))
  if vote_text:
    up, total = re.findall(re.compile(num_format), vote_text)
    review.upvote_count = int(up)
    review.downvote_count = int(total) - int(up)
  else:
    review.upvote_count = review.downvote_count = 0

  rating_text = dom.find(title=re.compile('[1-5]\.[0-5] out of [1-5] stars'))['title']
  review.rating = float(rating_text[:3])

  return review

def get_rank(html):
  """
  Parses a profile object based on an html string
  :param html: A string containing the html of a profile page
  :return: A profile object
  """
  dom = bs4.BeautifulSoup(html, 'html.parser')
  return int(dom.select('.bio-expander')[0].find(text=re.compile('#' + num_format))[1:].replace(',', ''))

def get_product(xml):
  """
  Parses a product object based on an xml string
  :param xml: A string containing the xml of an amazon response for a product
  :return: A product object
  """
  product = models.Product()
  dom = bs4.BeautifulSoup(xml, 'html.parser')
  xml = dom.itemlookupresponse.items.item

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
