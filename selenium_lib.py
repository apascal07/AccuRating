"""Selenium helper function library"""
import selenium
from selenium.webdriver.common import by


class SeleniumLib:
  """"""

  def __init__(self, b_type="Firefox"):
	if b_type is "Firefox":
		self.driver = selenium.webdriver.Firefox()
	else:
		self.driver = selenium.webdriver.Chrome()
    self.open_page('http://www.amazon.com')

  def open_page(self, url):
    """Opens the page with specified url"""
    self.driver.get(url)

  def scroll_into_view(self, element_id):
    """
    Scrolls the page so element with id element_id is in view
    """
    element = self.driver.find_element_by_id(element_id)
    self.driver.execute_script('return arguments[0].scrollIntoView()', element)

  def click_element(self, locator, value):
    """Clicks an element on the page
          locator - type of locator.
                    Acceptable values are ID and text
          value - string the locator should look for
    """
    locator_by_dict = {'ID': by.By.ID, 'text': by.By.LINK_TEXT}
    if locator in locator_by_dict:
      raise Exception("{} is not a valid locator.".format(locator))
    element = self.driver.find_element(by=locator_by_dict[locator], value=value)