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


def get_amazon_rating(html):
  pass


def get_page_count(html):
  pass


def get_review_urls(html):
  pass


def get_review(html):
  """
  Parses a review object based on an html string
  :param html: A string containing the html of a reviewer page
  :return: A parsed reviewer object
  """
  review = models.Review()
  soup = bs4.BeautifulSoup(html, 'html.parser')

  # parse the 'hReview' element that contains several needed pieces of data
  hidden_review = soup.find_all(class_='hReview')[0]

  review.text = hidden_review.find(class_='description').text
  review.verified = len(soup.find_all(class_='verifyWhatsThis')) > 0
  review.timestamp = filter(None, [_get_date(tag.text) for tag in soup.find_all('nobr')])[0]

  reviewer_element = hidden_review.find(class_='reviewer').find(class_='url')
  review.reviewer_url = 'http://www.amazon.com' + reviewer_element['href']

  vote_text = soup.find(text=re.compile(num_format + ' of ' + num_format +
                                        ' people found the following review helpful'))
  if vote_text:
    up, total = re.findall(re.compile(num_format), vote_text)
    review.upvote_count = int(up)
    review.downvote_count = int(total) - int(up)
  else:
    review.upvote_count = review.downvote_count = 0

  rating_text = soup.find(title=re.compile('[1-5]\.[0-5] out of [1-5] stars'))['title']
  review.rating = float(rating_text[:3])

  return review

def get_profile(html):
  """
  Parses a profile object based on an html string
  :param html: A string containing the html of a profile page
  :return: A profile object
  """
  profile = models.Reviewer()
  dom = bs4.BeautifulSoup(html, 'html.parser')

  profile.name = dom.find(class_='public-name-text').text
  profile.rank = int(dom.find(class_='bio-expander').find(text=re.compile('#' + num_format))[1:].replace(',', ''))
  profile.vote_count = int(dom.find(class_='bio-expander').find(text=re.compile(num_format)).replace(',', ''))
  date_str = dom.find_all(class_='glimpse-raw-timestamp').pop().text
  profile.creation_date = datetime.datetime.strptime(date_str, '%b %d, %Y')

  distribution = {i: 0 for i in range(1, 6)}
  ratings = dom.find_all('i', class_=re.compile('a-icon-star'))
  for rating in ratings:
    val = int(re.findall(re.compile('[0-5]'), ''.join(rating['class']))[0])
    distribution[val] += 1

  profile.rating_distribution = distribution

  return profile

def get_product(xml):
  """
  Parses a product object based on an xml string
  :param xml: A string containing the xml of an amazon response for a product
  :return: A product object
  """
  product = models.Product()
  soup = bs4.BeautifulSoup(xml, 'html.parser')
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
