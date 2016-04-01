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


def _select(element, query, important=True):
    result = element.select_one(query)
    if result is None and important:
        raise Exception('Element not found: {}'.format(query))
    return result


def _select_all(element, query, important=True):
    results = element.select(query)
    if results is [] and important:
        raise Exception('Element not found: {}'.format(query))
    return results


def _find(element, important=True, **kwargs):
    result = element.find(**kwargs)
    if result is None and important:
        raise Exception('Element not found: {}'.format(kwargs))
    return result


def _find_all(element, important=True, **kwargs):
    results = element.find_all(**kwargs)
    if results is [] and important:
        raise Exception('Element not found: {}'.format(kwargs))
    return results


def get_reviews_url(html):
  dom = bs4.BeautifulSoup(html, 'html.parser')
  return _select(dom, '.crIframeReviewList span.small > b > a')['href']


def get_amazon_rating(html):
  dom = bs4.BeautifulSoup(html, 'html.parser')
  return float(_select(dom, '.arp-rating-out-of-text').text[:3])


def get_page_count(html):
  dom = bs4.BeautifulSoup(html, 'html.parser')
  return int(_select_all(dom, '.page-button').pop().text)


def get_review_url_list(html):
  dom = bs4.BeautifulSoup(html, 'html.parser')
  titles = _select_all(dom, 'a.review-title')
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
  review.text = _select(dom, '.hReview .description').text
  review.verified = _select(dom, '.verifyWhatsThis', important=False) is not None
  review.timestamp = filter(None, [_get_date(tag.text) for tag in _select_all(dom, 'nobr')])[0]

  reviewer_element = _select(dom, '.hReview .reviewer .url')
  review.reviewer_url = 'http://www.amazon.com{}'.format(reviewer_element['href'])
  vote_regex = re.compile('{0} of {0} people found the following review helpful'.format(num_format))
  vote_text = _find(dom, text=vote_regex, important=False)
  if vote_text:
    up, total = re.findall(re.compile(num_format), vote_text)
    review.upvote_count = int(up)
    review.downvote_count = int(total) - int(up)
  else:
    review.upvote_count = review.downvote_count = 0

  rating_text = _find(dom, title=re.compile('[1-5]\.[0-5] out of [1-5] stars'))['title']
  review.rating = float(rating_text[:3])

  return review

def get_rank(html):
  """
  Parses a profile object based on an html string
  :param html: A string containing the html of a profile page
  :return: A profile object
  """
  dom = bs4.BeautifulSoup(html, 'html.parser')
  return int(_find(_select(dom, '.bio-expander'), text=re.compile('#' + num_format))[1:].replace(',', ''))

def get_product(xml):
  """
  Parses a product object based on an xml string
  :param xml: A string containing the xml of an amazon response for a product
  :return: A product object
  """
  dom = bs4.BeautifulSoup(xml, 'html.parser')
  product = models.Product()
  xml = _select(dom, 'itemlookupresponse > items > item')

  product.title = _select(xml, 'itemattributes > title').string
  product.product_url = _select(xml, 'detailpageurl').string
  product.reviews_url = _select(xml, 'customerreviews > iframeurl').string
  product.retrieval_date = datetime.datetime.today()
  product.category = _select(xml, 'itemattributes > productgroup').string

  # concatenate all description data
  features = _select_all(xml, 'itemattributes > feature')
  product.description = '. '.join([feature.string for feature in features]) + '. '
  for editorial_review in _select_all(xml, 'editorialreviews > editorialreview'):
    if editorial_review.source.string == 'Product Description':
      product.description += editorial_review.content.string

  return product
