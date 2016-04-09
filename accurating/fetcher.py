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
  def fetch_pages(self, urls, max_retries=10):
    """Retrieves the responses for each of the URLs passed in."""
    pages = []
    for url in urls:
      fetch_attempts = 1

      # Attempt to fetch the page. Retry if failed
      while True:
        try:
          self.driver.get(url)
          break
        except Exception as ee:
          if fetch_attempts < max_retries:
            logging.warn("Failed to fetch url='{}'. Retrying".format(url))
          else:
            logging.error("Failed to fetch url='{}': {}".format(url, ee))
            raise

      # Handle the page html
      pages.append(self.driver.page_source)
    return pages
