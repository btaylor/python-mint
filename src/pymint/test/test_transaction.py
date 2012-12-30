import unittest
from mint.transaction import Transaction
from mint import mint

TEST_TRANSACTION = {"isTransfer":False,"isBuy":False,"isLinkedToRule":False,"odate":"Sep 28","isSpending":True,"isCheck":False,"isFirstDate":True,"date":"Sep 28","mcategory":"Groceries","amount":"$31.99","id":214373746,"isDuplicate":False,"isSell":False,"fi":"CapitalOne","isChanged":False,"note":"","isAfterFiCreationTime":False,"ruleCategory":"","symbol":"","merchant":"Irvine Market","omerchant":"SUPER IRVINE MARKET IRVINE CA","categoryId":701,"labels":[{"id":143477,"name":"Reimbursable"},{"id":620386,"name":"X Home"}], "isInvestment":False,"shares":0,"category":"Groceries","ruleCategoryId":0,"numberMatchedByRule":7,"account":"World MasterCard","mmerchant":"Irvine Market","ruleMerchant":"","isChild":False,"isDebit":True,"isEditable":True }


class Test(unittest.TestCase):
    def test_tx(self):
        tx = Transaction.from_json(TEST_TRANSACTION, mint=mint)
        assert tx.mint == mint
        assert mint.tags['X Home'] in tx.tags
        assert mint.tags['Reimbursable'] in tx.tags

    def test_tx_reuse(self):
        tx1 = Transaction.from_json(TEST_TRANSACTION, mint=mint)
        tx2 = Transaction.from_json(TEST_TRANSACTION, mint=mint)
        assert id(tx1) == id(tx2)

    def test_diff(self):
        tx = Transaction.from_json(TEST_TRANSACTION, mint=mint)

        tx.tags.add(mint.tags['X Home'])
        diffs = tx.diff()
        assert len(diffs) == 0

        tx.tags.add(mint.tags['X BC'])
        diffs = tx.diff()
        assert 'tags' in diffs and len(diffs) == 1
        assert mint.tags['X BC'] in diffs['tags']['added']
        assert len(diffs['tags']['removed']) == 0

        tx.merchant = "LOL"
        diffs = tx.diff()
        assert 'merchant' in diffs and len(diffs) == 2

        
    def test_transactionset(self):
        txs = mint.transactions.filter(tag=mint.tags['X Home'])
        assert txs.query_string == 'tag: "X Home"'
        first_tx = iter(txs).next()

    def xtest_pyfilter(self):
        txs = mint.transactions.filter(tag=mint.tags['X Home']).pyfilter(tags__len=2)
        first_tx = iter(txs).next()
        print first_tx

        
        

