try:
    from google.appengine.api import urlfetch
except ImportError:
    from pymint import urlfetch
try:
    import json
except ImportError:
    import simplejson as json

import logging
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger('mint')
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
logger.setLevel(logging.DEBUG)
logger.addHandler(sh)
logger.propagate = False

def fetch_json(*args, **kwargs):
    return json.loads(urlfetch.fetch(*args, **kwargs).content)

class CachedIterable(object):
    def __init__(self, iterable):
        self.iterable = iterable
        self.cached = []

    def __iter__(self):
        for e in self.cached:
            yield e

        for e in self.iterable:
            self.cached.append(e)
            yield e

import weakref
from collections import defaultdict
class Flyweight(object):
    _pool = defaultdict(weakref.WeakValueDictionary)

    def __new__(cls, *args, **kwargs):
        id = args[0] if args else kwargs['id']
        obj = cls._pool[cls].get(id, None)
        
        if not obj:
            obj = object.__new__(cls)
            cls._pool[cls][id] = obj 
        else:
            pass #            logger.debug("Reusing %s %d" % (cls.__name__, id))

        return obj 
    
 
def isiterable(i):
    try:
        it = iter(i)
        return True
    except TypeError:
        return False

DATE_INPUT_FORMATS = (
    '%m-%d-%Y',              # '2006-10-25'
    '%m/%d/%Y',              # '10/25/2006'
    '%m/%d/%y',              #
    '%m %d %y',              #
    '%m %d %Y',              # 
    '%b %d %y',              #
    '%b %d %Y',              # 
)

def extract_element(xml, element):
    start, end = "<%s>" % element, "</%s>" % element
    i = xml.find(start)+len(start)
    j = xml.find(end, i)
    return xml[i:j]

import datetime
CURRENT_YEAR = datetime.datetime.now().year
def parse_date(date, year=CURRENT_YEAR):
    for format in DATE_INPUT_FORMATS:
        try:
            return datetime.datetime.strptime(date, format)
        except ValueError:
            try:
                return datetime.datetime.strptime("%s %s" % (date, year), format)
            except ValueError:
                pass
    raise ValueError("Couldn't parse date from %s" % date)

