"""Scraper extracts data from raw HTML and creates corresponding objects."""
import models
from bs4 import BeautifulSoup
import engine


@engine.timer
def get_page_count(html):
  pass


@engine.timer
def get_review_urls(html):
  pass


@engine.timer
def get_review(html):
  pass


@engine.timer
def get_profile(html):
  pass


@engine.timer
def get_product(html):
  soup = BeautifulSoup(html, "html.parser")
  product_xml = soup.itemlookupresponse.items.item
  print product_xml.title.text
