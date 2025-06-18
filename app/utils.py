import os
import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def is_valid_url(url):
    import re
    pattern = re.compile(r'^https?://')
    return bool(pattern.match(url))
