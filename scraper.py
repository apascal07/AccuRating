"""Scraper extracts data from raw HTML and creates corresponding objects."""
import models
import bs4

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
  return product
