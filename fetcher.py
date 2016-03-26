"""Fetcher retrieves remote pages from the Amazon platform."""

import logging
import re

import bs4
import amazonproduct
from amazonproduct import errors
from amazonproduct import processors
from google.appengine.api import urlfetch


class SoupProcessor (processors.BaseProcessor):
  """
  Custom response parser using BeautifulSoup to parse the returned XML.
  """

  def parse(self, fp):

    soup = bs4.BeautifulSoup(fp.read(), 'html.parser')

    # parse errors
    for error in soup.findAll('error'):
        code = error.find('code').text
        msg = error.find('message').text
        raise errors.AWSError(code, msg)

    return soup

class PageFetcher:
  """Fetches the html for a specified page"""
  def __init__(self):
    self.api = amazonproduct.API(locale='us', cfg='lib/.amazon-product-api', processor=SoupProcessor())

  def fetch_product(self, asin):
    # Fetch the product description.
    return self.api.item_lookup(asin, ResponseGroup='EditorialReview', paginate=False)

  def fetch_pages(self, urls):
    """Generic function to fetch multiple pages at once"""
    num_requests = 0
    max_requests = 100
    results = []
    # Break the urls into groups of *max_requests* to prevent sending out too many requests at once
    url_groups = [urls[x:x + max_requests] for x in xrange(0, len(urls), 100)]
    for url_group in url_groups:
      results.extend(self._fetch_pages(url_group))
    return results

  def _fetch_pages(self, urls):
    """Helper function that makes the page fetch request and waits for the response"""
    rpcs = []
    results = []
    # Set the headers to appear as if we are using a real browser.
    # Appengine plays with these results to state the request is coming from Appengine
    hdr = {
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
      'Accept-Encoding': 'none',
      'Accept-Language': 'en-US,en;q=0.8',
      'Connection': 'keep-alive'}

    try:
      # Fetch all urls asynchronously
      for url in urls:
        rpc = urlfetch.create_rpc()
        rpcs.append(rpc)
        urlfetch.make_fetch_call(rpc, url, headers=hdr)
      # Process all of the responces
      for rpc in rpcs:
        rpc.wait()
        results.append(rpc.get_result().content)

      return results
    except Exception as eee:
      raise Exception("Failed to fetch page: {}".format(eee))

  def fetch_profiles(self, urls):
    """Uses loads all the reviews on the profile page and returns the final page html"""

    pattern = '(<div data-glimpse_path.*?>)'
    pages = []
    complete_pages = []
    try:
      # First set of responses if for the original profile page.
      # The next set of urls is different than for the remaining pages.
      responses = self.fetch_pages(urls)
      for i, response in enumerate(responses):
        pages.append(response)
        tag = self._get_div_tag_contents(response, pattern)

        urls[i] = "http://www.amazon.com/{}".format(tag['data-glimpse_path'])

      pattern = '^(<div class="glimpse-main-pagination-trigger".*?<\/div>)'
      # Fetch all remaining pages
      while urls:
        responses = self.fetch_pages(urls)
        for i, page in enumerate(responses):
          tag = self._get_div_tag_contents(page, pattern)

          if tag['data-pagination-token']:
            tag['data-pagination-token'] = tag['data-pagination-token'].replace('=', '')

            urls[i] = ('{}?token={}%3D%3D&context={}&id={}&preview='.
                       format(tag['data-url'], tag['data-pagination-token'], tag['data-feed-context'],
                              tag['data-feed-id'], tag['data-preview-mode']))
            pages[i] = pages[i] + "\n" + page
          else:
            urls.pop(i)
            complete_pages.append(pages.pop(i))
      return complete_pages
    except Exception as eee:
      raise Exception('Failed to fetch user profiles: {}'.format(eee))

  def _get_div_tag_contents(self, html, pattern):
    """"""
    matches = re.findall(pattern, html, re.MULTILINE | re.DOTALL)

    if matches:
      soup = bs4.BeautifulSoup(matches[0], 'html.parser')
      return soup.div
    raise Exception("Expected to find a match for pattern {}".format(pattern))

