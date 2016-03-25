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
import scraper
import pprint

class MainHandler(webapp2.RequestHandler):
    def get(self):
        logging.info('hello world!')
        self.response.write('Hello world!')

class ScraperHandler(webapp2.RequestHandler):
    def get(self):
        pp = pprint.PrettyPrinter(indent=4)

        product = open('./test_files/product.xml').read()
        self.response.write('<b>Get product: </b><br />')
        self.response.write(pp.pformat(scraper.get_product(product)))
        self.response.write('<br /><br />')

        review = open('./test_files/review.html').read()
        self.response.write('<b>Get review: </b><br />')
        self.response.write(pp.pformat(scraper.get_review(review)))
        self.response.write('<br /><br />')

        profile = open('./test_files/profile.html').read()
        self.response.write('<b>Get profile: </b><br />')
        self.response.write(pp.pformat(scraper.get_profile(profile)))
        self.response.write('<br /><br />')

        reviews_iframe = open('./test_files/reviews_iframe.html').read()
        self.response.write('<b>Get reviews url: </b>')
        self.response.write(pp.pformat(scraper.get_reviews_url(reviews_iframe)))
        self.response.write('<br /><br />')

        review_list = open('./test_files/review_list.html').read()
        self.response.write('<b>Get page count: </b>')
        self.response.write(pp.pformat(scraper.get_page_count(review_list)))
        self.response.write('<br /><br /><b>Get amazon rating: </b>')
        self.response.write(pp.pformat(scraper.get_amazon_rating(review_list)))
        self.response.write('<br /><br /><b>Get review URL list: </b><br />')
        self.response.write(pp.pformat(scraper.get_review_url_list(review_list)))


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/scraper', ScraperHandler)
], debug=True)
