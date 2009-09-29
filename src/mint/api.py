from mint.utils import *
from mint.tags import *
from mint.transaction import *
import time

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
        Mint.get_url('logout.event')
        self.clear()
        self.logged_in = False

    def clear(self):
        self._data = None

    @property
    @require_login
    def data(self):
        if getattr(self, '_data', None):
            return self._data
        response = json.loads(Mint.get_url('getJsonData.xevent', {'task' : 'tags,categories', 'token' : self.token}).content)
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
    def format_url(event):
        return 'https://wwws.mint.com/%s' % event

    @staticmethod
    def get_url(event, *args, **kwargs):
        ret = urlfetch.fetch(Mint.format_url(event), *args, **kwargs)
        if ret.content.find('Internal Error') != -1:
            ret.status_code = 500
        return ret
 
    @staticmethod
    def post_url(*args, **kwargs):
        kwargs['method'] = urlfetch.POST
        return Mint.get_url(*args, **kwargs)
 
    @require_login       
    def export_all(self):
        import csv
        response = Mint.get_url('transactionDownload.event')
        return csv.DictReader(StringIO(response.content))

    @property
    @require_login
    def transactions(self):
        params = {'task' : 'transactions', 'offset' : 0}
        prev_date = datetime.datetime.now()
        while True:
            response = json.loads(Mint.get_url('getJsonData.xevent', params).content)
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

    def get_or_create_tag(self, value):
        for tag in self.tags:
            if tag.value == value:
                return tag, False
        return self.create_tag(value), True
 
    def create_tag(self, value):       
        d = {'task' : 'C', 'token' : self.token, 'nameOfTag' : value}
        response = Mint.post_url('updateTag.xevent', d)
        assert response.status_code == 200, response.content
        try:
            tagId = int(extract_element(response.content, 'tagId'))
        except ValueError:
            raise ValueError("Bad response: %s" % response.content)
        self.tags.add(Tag(tagId, value, mint=self))
        return self.tags[value]

    def delete_tag(self, tagId):
        d = {'task' : 'D', 'token' : self.token, 'tagId' : tagId}
        response = Mint.post_url('updateTag.xevent', d)
        assert response.status_code == 200
        tagId = int(extract_element(response.content, 'tagId'))
        self.clear()


