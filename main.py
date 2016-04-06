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


def _pstring(dict):
  s = ''
  for k, v in dict.iteritems():
    s += '<b>{}</b>: {}<br />'.format(k, v)
  return s


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
  def get(self, asin):
    fetch = fetcher.PageFetcher()

    self.response.write(fetch.fetch_product(asin))

    product = open('./test_files/product.xml').read()
    self.response.write('<b><u>Get product: </b></u><br />')
    self.response.write(_pstring(scraper.get_product(fetch.fetch_product(asin)).__dict__['_values']))
    self.response.write('<br /><br />')

    review = open('./test_files/review.html').read()
    self.response.write('<b><u>Get review: </b></u><br />')
    self.response.write(_pstring(scraper.get_review(review).__dict__['_values']))
    self.response.write('<br /><br />')

    profile = open('./test_files/profile.html').read()
    self.response.write('<b><u>Get rank: </b></u>')
    self.response.write(scraper.get_rank(profile))
    self.response.write('<br /><br />')

    reviews_iframe = open('./test_files/reviews_iframe.html').read()
    self.response.write('<b><u>Get reviews url: </b></u>')
    self.response.write(scraper.get_reviews_url(reviews_iframe))
    self.response.write('<br /><br />')

    review_list = open('./test_files/review_list.html').read()
    self.response.write('<b><u>Get page count: </b></u>')
    self.response.write(scraper.get_page_count(review_list))
    self.response.write('<br /><br /><b><u>Get amazon rating: </b></u>')
    self.response.write(scraper.get_amazon_rating(review_list))
    self.response.write('<br /><br /><b><u>Get review URL list: </b></u><br />')
    self.response.write(scraper.get_review_url_list(review_list))


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
    ('/scraper/(.+)', ScraperHandler),
    ('/search/(.+)', SearchHandler),
    ('/fetcher', FetcherHandler)
], debug=True)
