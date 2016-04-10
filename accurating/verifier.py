import models


def verify(ssids):
    """
    Runs verification analysis on a set of products
    :param ssids: SSIDs for the products to run the analysis on
    :return: A dictionary with the following fields:
        average_accurating_error: The average difference between Amazon's rating and the accurating
        average_simple_error: The average difference between Amazon's rating and the simple rating
        percent_requirements_met: The average number of products that met the requirements
    """
    simple_total = accurating_total = requirements_met_total = 0
    for ssid in ssids:
        product = models.Product.get_or_create_product(ssid)
        simple_error = abs(product.average_rating - product.amazon_rating)
        accurating_error = abs(product.weighted_rating - product.amazon_rating)
        simple_total += simple_error
        accurating_total += accurating_error
        if accurating_error < simple_error:
            requirements_met_total += 1

    return {
        'average_accurating_error': accurating_total / len(ssids),
        'average_simple_error': simple_total / len(ssids),
        'percent_requirements_met': requirements_met_total / len(ssids)
    }
