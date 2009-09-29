from mint.utils import *
from mint.tags import *
from mint.transaction import *

import csv
from StringIO import StringIO

def require_login(fn):
    def inner(self, *args, **kwargs):
        if not self.logged_in:
            raise ValueError("Not logged in!")
        return fn(self, *args, **kwargs)
    return inner


class Mint(object):
    def __init__(self):
        self.logged_in = False

    def login(self, username, password):
        response = urlfetch.fetch('https://wwws.mint.com/login.event', {'username' : username, 'password' : password, 'task' : 'L'}, method=urlfetch.POST)
        try:
            self.token = Mint.get_token(response)
            self.logged_in = True
        except ValueError:
            raise 

    def logout(self):
        Mint.fetch_url('logout.event')
        self.clear()
        self.logged_in = False

    def clear(self):
        self._data = None

    @property
    def data(self):
        if getattr(self, '_data', None):
            return self._data
        response = fetch_json(Mint.get_url('getJsonData.xevent'), {'task' : 'tags,categories'})
        self._data = {}
        for set in response['set']:
            self._data[set['id']] = set['data']
        return self._data

    @staticmethod
    def get_token(response):
        content = response.content
        i = content.find('"', content.find('value=', content.find('id="javascript-token"'))) + 1
        j = content.find('"', i)
        if i == j:
            raise ValueError("No token")
        return content[i:j]

    @staticmethod
    def get_url(event):
        return 'https://wwws.mint.com/%s' % event

    @staticmethod
    def fetch_url(event):
        return urlfetch.fetch(Mint.get_url(event))
        
 
    @require_login       
    def export_all(self):
        import csv
        response = Mint.fetch_url('transactionDownload.event')
        return csv.DictReader(StringIO(response.content))

    @property
    @require_login
    def transactions(self):
        params = {'task' : 'transactions', 'offset' : 0}
        prev_date = datetime.datetime.now()
        while True:
            response = fetch_json(Mint.get_url('getJsonData.xevent'), params)
            data = response['set'][0]['data']
            if len(data) == 0:
                break
            for datum in data:
                tx = Transaction.from_json(datum, mint=self, year=prev_date.year)
                if tx.date > prev_date:
                    tx.date = datetime.datetime(tx.date.year-1, tx.date.month, tx.date.day)
                    raise ValueError("is this correct?")
                prev_date = tx.date
                yield tx
                params['offset'] += 1

    @property
    @require_login
    def tags(self):
        if getattr(self, '_tags', None):
            return self._tags
        self._tags = TagSet.from_json(self.data['tags'], mint=self)
        return self._tags
