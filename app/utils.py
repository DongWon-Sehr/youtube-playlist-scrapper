import os

ROOT_DIR = os.path.expanduser('~/Documents/PoPo')

def resource_path(relative_path):
    import os
    import sys
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def is_valid_url(url):
    import re
    pattern = re.compile(r'^https?://')
    return bool(pattern.match(url))

def get_host(url):
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

def get_full_url(host, uri):
    from urllib.parse import urljoin
    return urljoin(host, uri)