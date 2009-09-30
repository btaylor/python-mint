from mint.utils import *
from mint.transaction import *

def run(d):
    from mint import mint
    filters = []
    for key, value in d.items():
        if key.startswith('mint_') and callable(value):
            filters.append(value)
    logger.debug("Got %d filters" % len(filters))
    mint.login(d['username'], d['password'])
    for f in filters:
        f(mint)
    Transaction.commit_dirty()
    mint.logout()
    
