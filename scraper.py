"""Scraper extracts data from raw HTML and creates corresponding objects."""
import models
import bs4
import datetime
import re


def _get_valid_time(time_str):
  re.sub(' (\d) ', ' 0{} ', time_str)
  try:
    return datetime.datetime.strptime(time_str, '%B %d, %Y')
  except ValueError:
    return None



def get_page_count(html):
  pass


def get_review_urls(html):
  pass


def get_review(html):
  review = models.Review()
  soup = bs4.BeautifulSoup(html, 'html.parser')
  hidden_review = soup.find_all(class_='hReview')[0]

  review.text = hidden_review.find(class_='description').text
  review.verified = len(soup.find_all(class_='verifyWhatsThis')) > 0
  review.timestamp = filter(None, [_get_valid_time(tag.text) for tag in soup.find_all('nobr')])[0]

  reviewer_element = hidden_review.find(class_='reviewer').find(class_='url')
  review.reviewer = reviewer_element.text
  review.reviewer_url = 'http://www.amazon.com' + reviewer_element['href']

  vote_text = soup.find(text=re.compile('\d+ of \d+ people found the following review helpful'))
  up, total = re.findall(r'\d+', vote_text)
  review.upvote_count = int(up)
  review.downvote_count = int(total) - int(up)

  rating_text = soup.find(title=re.compile('\d\.\d out of \d stars'))['title']
  review.rating = float(rating_text[:3])

  return soup.find_all(class_='hReview')

def get_profile(html):
  pass


def get_product(html):
  product = models.Product()
  soup = bs4.BeautifulSoup(html, 'html.parser')
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
