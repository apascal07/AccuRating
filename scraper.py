"""Scraper extracts data from raw HTML and creates corresponding objects."""
import models
from bs4 import BeautifulSoup

def get_page_count(html):
  pass


def get_reviews(html):
  pass


def get_profile(html):
  pass


def get_product(html):
  soup = BeautifulSoup(html, "html.parser")
  product_xml = soup.itemlookupresponse.items.item
  print product_xml.title.text