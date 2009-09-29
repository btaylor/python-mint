import unittest
from mint.transaction import Transaction
import mint

TEST_TRANSACTION = {"isTransfer":False,"isBuy":False,"isLinkedToRule":False,"odate":"Sep 28","isSpending":True,"isCheck":False,"isFirstDate":True,"date":"Sep 28","mcategory":"Groceries","amount":"$31.99","id":214373746,"isDuplicate":False,"isSell":False,"fi":"CapitalOne","isChanged":False,"note":"","isAfterFiCreationTime":False,"ruleCategory":"","symbol":"","merchant":"Irvine Market","omerchant":"SUPER IRVINE MARKET IRVINE CA","categoryId":701,"labels":[{"id":143477,"name":"Reimbursable"},{"id":620386,"name":"X Mom & Dad"}], "isInvestment":False,"shares":0,"category":"Groceries","ruleCategoryId":0,"numberMatchedByRule":7,"account":"World MasterCard","mmerchant":"Irvine Market","ruleMerchant":"","isChild":False,"isDebit":True,"isEditable":True }


class Test(unittest.TestCase):
    def test_tx(self):
        tx = Transaction.from_json(TEST_TRANSACTION, mint=mint.mint)
        assert tx.mint == mint.mint
        assert mint.mint.tags['X Mom & Dad'] in tx.tags
        assert mint.mint.tags['Reimbursable'] in tx.tags
        
           
