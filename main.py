#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import logging
import search
import scraper
import fetcher
import pprint
import cgi


def _pstring(obj):
  s = ''
  try:
    for k, v in obj.__dict__['_values'].iteritems():
      s += '<b>{}</b>: {}<br />'.format(k, v)
    return s
  except (KeyError, AttributeError):
    return obj


class MainHandler(webapp2.RequestHandler):
  def get(self):
    logging.info('hello world!')
    self.response.write('Hello world!')


class SearchHandler(webapp2.RequestHandler):
  def get(self, asin):
    logging.info('Running search handler.')
    product = search.get_product(asin)
    pprint.pprint(product)
    self.response.write(product)


class ScraperHandler(webapp2.RequestHandler):
  def get(self):
    params = self.request.GET
    fetch = fetcher.PageFetcher()

    if params['product']:
      product = scraper.get_product(fetch.fetch_product(params['product']))
      reviews_url = scraper.get_reviews_url(fetch.fetch_pages([product.reviews_url])[0])
      review_list = fetch.fetch_pages([reviews_url])[0]
      if 'review' in params:
        review_url = 'http://www.amazon.com/review/{}'.format(params['review'])
      else:
        review_url = scraper.get_review_url_list(review_list)[0]
      review = scraper.get_review(fetch.fetch_pages([review_url])[0])

      results = {
          'Get product': product,
          'Get reviews url': reviews_url,
          'Get Page count': scraper.get_page_count(review_list),
          'Get Amazon Rating': scraper.get_amazon_rating(review_list),
          'Get Review URL List': scraper.get_review_url_list(review_list),
          'Get Review': review,
          'Get Rank': scraper.get_rank(fetch.fetch_pages([review.reviewer_url])[0])
      }

      for val in results:
        self.response.write('<b><u>{}:</b></u> {}<br />'.format(val, _pstring(results[val])))


class FetcherHandler(webapp2.RequestHandler):
  def get(self):
    review_url = ('http://www.amazon.com/review/R295DL2GL6DDJU/ref=cm_cr_dp_title?ie=UTF8&ASIN=B00I15SB16'
                  '&channel=detail-glance&nodeID=370783011&store=amazon-ereaders')
    fetch = fetcher.PageFetcher()
    logging.info('\n')

    #self.response.write(fetch.fetch_product('B00I15SB16'))
    logging.info('\n')
    logging.info('\n')
    logging.info('\n')
    #self.response.write(fetch.fetch_pages([review_url])[0])
    logging.info('\n')
    logging.info('\n')
    logging.info('\n')
    self.response.write(fetch.fetch_profiles(["http://www.amazon.com/gp/pdp/profile/A1AZ7G19GEHCFB/ref=cm_cr_dp_pdp"]))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/search/(.+)', SearchHandler),
    ('/scraper', ScraperHandler),
    ('/fetcher', FetcherHandler)
], debug=True)
