try:
    from google.appengine.api import urlfetch
except ImportError:
    from mint import urlfetch
import json

def fetch_json(*args, **kwargs):
    return json.loads(urlfetch.fetch(*args, **kwargs).content)



DATE_INPUT_FORMATS = (
    '%m-%d-%Y',              # '2006-10-25'
    '%m/%d/%Y',              # '10/25/2006'
    '%m/%d/%y',              #
    '%m %d %y',              #
    '%m %d %Y',              # 
    '%b %d %y',              #
    '%b %d %Y',              # 
)

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

