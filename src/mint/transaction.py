import datetime
import urlfetch
import copy
from mint.tags import *
from mint.utils import *

class TransactionSet(object):
    def __init__(self, mint, query_string='', pyfilters=[]):
        self.mint = mint
        self.query_string = query_string
        self.pyfilters = pyfilters

    def filter(self, query=None, description=None, tag=None, category=None):
        queries = []
        if self.query_string:
            queries.append(self.query_string)
        if query:
            queries.append(query)
        if description:
            queries.append('description:"%s"' % description)
        if tag:
            queries.append('tag:"%s"' % tag.name)
        if category:
            queries.append('category:"%s"' % category)
        query = "  ".join(queries)
        return TransactionSet(self.mint, query)
    
    @staticmethod
    def get_filter_fn(fn=None, **kwargs):
        fns = [fn] if fn else []
        for key, value in kwargs.items():
            if key == 'tag':
                fns.append(lambda tx: value in tx.tags)
            elif key == 'tags__len':
                fns.append(lambda tx: len(tx.tags) == value)
            elif key == 'description':
                fns.append(lambda tx: tx.merchant.find(value) != -1)
            elif key == 'category':
                fns.append(lambda tx: tx.category.find(value) != -1)
            else:
                raise ValueError("filter '%s' not recognized" % key)
        return lambda tx: all(fn(tx) for fn in fns)

    def pyfilter(self, **kwargs):
        fn = TransactionSet.get_filter_fn(**kwargs)
        return TransactionSet(self.mint, self.query_string, self.pyfilters + [fn])
        
    def pyexclude(self, **kwargs):
        fn_ = TransactionSet.get_filter_fn(**kwargs)
        fn = lambda tx: not fn_(tx)
        return TransactionSet(self.mint, self.query_string, self.pyfilters + [fn])
        
    def __iter__(self):
        for transaction in self.mint.get_transactions(query=self.query_string):
            if all(fn(transaction) for fn in self.pyfilters):
                yield transaction

    def add_tag(self, tag):
        for tx in self:
            tx.tags.add(tag)

    def remove_tag(self, tag):
        for tx in self:
            tx.tags.remove(tag)

    def commit(self):
        for tx in self:
            tx.commit()
            

MAPPING = {
    'Description' : 'description',
    'Original Description' : 'original_description',
    'Amount' : 'amount',
    'Transaction Type' : 'transaction_type',
    'Category' : 'category',
    'Account Name' : 'account_name',
    'Notes' : 'notes',
}

JSON_KEYS = ['amount', 'id', 'note', 'merchant', 'omerchant', 'categoryId', 'category', 'fi', 'account']

import weakref
class Transaction(Flyweight):
    @classmethod
    def commit_dirty(cls):
        for v in cls._pool[cls].values():
            v.commit()

    @staticmethod
    def from_json(data, mint, year=None):
        d = {'mint' : mint}
        d['date'] = parse_date(data['date'], year or datetime.datetime.now().year)
        d['tags'] = TagSet.from_json(data['labels'], name_key='name', mint=mint)
        for key in JSON_KEYS:
            d[key] = data[key]
        return Transaction(**d)

    def __init__(self, **kwargs):
        if self.diff():
            return self.update(**kwargs)

        self.mint = kwargs.pop('mint', None)
        self.originals = {}
        for key, value in kwargs.items():
            setattr(self, key, value)
            self.originals[key] = copy.copy(value)

    def update(self, **kwargs):
        return

    def diff(self):
        if not getattr(self, 'originals', None):
            return {}

        k = object()
        diffs = {}
        for key, value in self.originals.items():
            if value == getattr(self, key, k):
                continue
            diffs[key] = (value, getattr(self, key, None))
        if 'tags' in diffs:
            orig, new = diffs['tags'] 
            added, removed = orig.diff(new)
            diffs['tags'] = {'added' : added, 'removed' : removed}
        return diffs
                

    def __repr__(self):
        return '<Transaction: %s>' % unicode(self)

    def __unicode__(self):
        return "%s %s" % (self.merchant, self.date.strftime("%m-%d-%Y"))

    def commit(self, force=False):
        diff = self.diff()
        if not diff and not force:
            logger.debug("Not committing %s: %s" % (self, diff))
            return False

        d = {'task' : 'txnedit', 'txnId' : "%s:false" % self.id, 'token' : self.mint.token}

        tags = diff.pop('tags', {})
        added, removed = tags.get('added', []), tags.get('removed', [])
        for tag in self.mint.tags:
            value = 2 if tag in added else (0 if tag in removed else 1)
            d['tag%d' % tag.id] = value
            
        for key, value in diff.items():
            d[key] = value[1]

        logger.warning("Committing %s" % self)
        logger.debug("Commit data: %s" % d)
        response = self.mint.post_url('updateTransaction.xevent', d)
        return response

