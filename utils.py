def convert_price_to_number(price):
    """
    Converts for example a string of 1 122,99
     to a float of 1122.99
    """
    import re

    rep = {',': '.', ' ': ''}
    rep = dict((re.escape(k), v) for k, v in rep.items())

    pattern = re.compile('|'.join(rep.keys()))
    return float(pattern.sub(lambda m: rep[re.escape(m.group(0))], price))
