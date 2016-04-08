"""Scraper extracts data from raw HTML and creates corresponding objects."""
import models
import bs4
import datetime
import re

num_format = '(\d+(?:\,\d{3})*)'


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
  """
  Gets the URL of a product's reviews
  :param html: The HTML of the product's review iFrame
  :return: The URL of the product's reviews
  """
  dom = bs4.BeautifulSoup(html, 'html.parser')
  return _select(dom, '.crIframeReviewList span.small > b > a')['href']


def get_amazon_rating(html):
  """
  Gets the amazon rating of a product
  :param html: A string containing the html of a product ratings page
  :return: The amazon rating of a product as a double
  """
  dom = bs4.BeautifulSoup(html, 'html.parser')
  return float(_select(dom, '.arp-rating-out-of-text').text[:3])


def get_page_count(html):
  """
  Gets the number of review pages belonging to a product
  :param html: A string containing the html of a product ratings page
  :return: Number of pages as an int
  """
  dom = bs4.BeautifulSoup(html, 'html.parser')
  page_buttons = _select_all(dom, '.page-button', important=False)
  if page_buttons:
    return int(page_buttons.pop().text)
  else:
    return 1


def get_review_url_list(html):
  """
  Returns a list of URLs that link to amazon reviews
  :param html: A string containing the html of a product ratings page
  :return: A list of URL strings
  """
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
  review.text = _select(dom, '.reviewText').text
  review.verified = _select(dom, '.verifyWhatsThis', important=False) is not None
  dates = [_get_date(tag.text) for tag in _select_all(dom, 'nobr')]
  review.timestamp = filter(None, dates)[0]

  reviewer_element = _select(dom, '.hReview .reviewer .url')
  review.reviewer_url = 'http://www.amazon.com{}'.format(reviewer_element['href'])
  vote_text = _select(dom, '.reviewText').parent.find('div', text=re.compile('^\s+{0} of {0} .+'.format(num_format)))

  if vote_text:
    up, total = re.findall(re.compile(num_format), vote_text.text)
    review.upvote_count = int(up)
    review.downvote_count = int(total) - int(up)
  else:
    review.upvote_count = review.downvote_count = 0

  rating_text = _find(dom, title=re.compile('[1-5]\.[0-5] out of 5 stars'))['title']
  review.rating = float(rating_text[:3])

  return review

def get_rank(html):
  """
  Parses a profile object based on an html string
  :param html: A string containing the html of a profile page
  :return: A profile object
  """
  dom = bs4.BeautifulSoup(html, 'html.parser')
  bio = _select(dom, '.bio-expander', important=False)
  if bio:
    return int(_find(bio, text=re.compile('#' + num_format))[1:].replace(',', ''))
  else:
    return None


def get_product(xml):
  """
  Parses a product object based on an xml string
  :param xml: A string containing the xml of an amazon response for a product
  :return: A product object
  """
  dom = bs4.BeautifulSoup(xml, 'html.parser')
  xml = _select(dom, 'itemlookupresponse > items > item')
  product = models.Product(id=_select(xml, 'asin').text)

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