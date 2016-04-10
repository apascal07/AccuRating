import abstract
import amazonproduct
import bs4
import common
import logging
import os
from amazonproduct import processors, errors
from selenium import webdriver


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
API_KEY_PATH = os.path.join(BASE_DIR, 'accurating', 'amazon-product-api.cfg')


class SoupProcessor(processors.BaseProcessor):

  def parse(self, file):
    soup = bs4.BeautifulSoup(file.read(), 'html.parser')
    for error in soup.findAll('error'):
      code = error.find('code').text
      message = error.find('message').text
      raise errors.AWSError(code, message)
    return soup


class PageFetcher(abstract.AbstractPageFetcher):

  def __init__(self):
    self.driver = webdriver.Firefox()
    self.driver.set_page_load_timeout(10)
    self.api = amazonproduct.API(locale='us', cfg=API_KEY_PATH,
                                 processor=SoupProcessor())

  @common.timer
  def fetch_product(self, asin):
    """Retrieves the Amazon API response for the given item lookup."""
    response_groups = ['EditorialReview', 'ItemAttributes', 'Reviews']
    response = self.api.item_lookup(
        asin, ResponseGroup=', '.join(response_groups), paginate=False)
    return str(response)

  @common.timer
  def fetch_page(self, url, max_retries=10):
    """Retrieves the responses for the given URL."""
    page_source = None
    for _ in range(max_retries):
      try:
        self.driver.get(url)
        page_source = self.driver.page_source
        break
      except Exception:
        logging.warn('Failed to fetch URL {}. Retrying...'.format(url))
    if not page_source:
      self.driver.close()
      raise Exception('Failed to fetch URL {} after {} attempts.'.format(
          url, max_retries))
    return page_source

  @common.timer
  def fetch_pages(self, urls, max_retries=10):
    """Retrieves the responses for the given URLs."""
    return [self.fetch_page(url, max_retries) for url in urls]
