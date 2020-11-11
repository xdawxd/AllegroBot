def convert_price_to_number(price: str):
    """
    Converts for example a string of 1 122,99
     to a float of 1122.99.
    """
    import re

    rep = {',': '.', ' ': ''}
    rep = dict((re.escape(k), v) for k, v in rep.items())

    pattern = re.compile('|'.join(rep.keys()))
    return float(pattern.sub(lambda m: rep[re.escape(m.group(0))], price))


def value_strip(tag: str, searched: str):
    """
    Strips a tag off a value and returns it.
    """
    import re

    try:
        strip_re = re.compile(rf'(-{tag}\s*)(\d*)')
        value = float(strip_re.search(str(searched)).group(2))

        return value
    
    except AttributeError:
        
        return None


def search_strip(searched: str):
    """
    Strips a tag and a value off a search and returns it.
    """
    import re

    strip_re = re.findall(r'(-p\s*)(\d*)', searched, re.I)

    temp = [''.join(''.join(j)) for j in [i for i in strip_re]]

    return searched.strip(' '.join(temp))
