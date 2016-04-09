"""Parser quantifies the quality of a review text with a scalar value."""

import abstract


class TextParser(abstract.AbstractTextParser):

  def __init__(self, reviews, product_description):
    self.reviews = reviews
    self.product_description = product_description

  def get_text_quality(self, text):
    """Quantifies the quality of a review text with a scalar value."""
    return 0
