import abc


class AbstractPageFetcher():

  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def fetch_product(self, asin):
    pass

  @abc.abstractmethod
  def fetch_pages(self, urls):
    pass


class AbstractTextParser():

  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def get_text_quality(self, text):
    pass
