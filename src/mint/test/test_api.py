from mint.api import Mint
from mint import mint
import unittest
from itertools import islice

class Test(unittest.TestCase):
    def xtest_export(self):
        results = mint.export_all()
        result = results.next()
        for key in 'Date,Description,Original Description,Amount,Transaction Type,Category,Account Name,Labels,Notes'.split(','):
            assert key in result
        
    def test_tags(self):
        for r in mint.tags:
            assert r.id > 0

    def test_transactions(self):
        import datetime
        old_date = datetime.datetime.now()
        for t in islice(mint.transactions, 40):
            assert t.date <= old_date
            old_date = t.date
#        assert False       
            
        
