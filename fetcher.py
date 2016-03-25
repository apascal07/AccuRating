"""Fetcher retrieves remote pages from the Amazon platform."""

from google.appengine.api import urlfetch
import selenium_lib


class PageFetcher:
  """"""
  def __init__(self):
    pass

  def fetch_product(self, asin):
    pass

  def fetch_pages(self, urls):
    """Generic function to fetch multiple pages at once"""
    num_requests = 0
    max_requests = 100
    results = []
    url_groups = [urls[x:x+max_requests] for x in xrange(0, len(urls), 100)]
    for url_group in url_groups:
      results.extend(self._fetch_pages(url_group))
    return results

  def _fetch_pages(self, urls):
    """Helper function that makes the page fetch request and waits for the response"""
    rpcs = []
    results = []

    for url in urls:
      rpc = urlfetch.create_rpc()
      rpcs.append(rpc)
      urlfetch.make_fetch_call(rpc, url)
    for rpc in rpcs:
      rpc.wait()
      results.append(rpc.get_result().content)

    return results

  def fetch_profile(self, url):
    """Uses selenium to load all the reviews on the profile page and returns the final page html"""
    try:
      browser = selenium_lib.SeleniumLib()
      browser.open_page(url)
      while True:
        refresh_el = browser.driver.find_element_by_class_name("glimpse-main-pagination-trigger")
        if refresh_el.get_attribute('token'):
          browser.scroll_into_view(id, "refresh")
    except Exception as eee:
      pass

    return refresh_el.get_attribute("outerHTML")
