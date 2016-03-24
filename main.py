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
import os

class MainHandler(webapp2.RequestHandler):
    def get(self):
        logging.info('hello world!')
        self.response.write('Hello world!')

class ScraperHandler(webapp2.RequestHandler):
    def get(self):
        html = open('./test_files/product.xml').read()
        self.response.write(scraper.get_product(html))


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/scraper', ScraperHandler)
], debug=True)
