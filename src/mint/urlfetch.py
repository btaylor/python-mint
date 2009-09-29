import urllib, urllib2, logging
urllib2.install_opener(urllib2.build_opener(urllib2.HTTPCookieProcessor()))

GET = object()
POST = object()

class URLFetchResponse(object):
    def __init__(self, response):
        self.content = response.read()
        self.status_code = response.getcode()
        self.headers = response.headers

def fetch(url, payload=None, method=GET, headers={}, allow_truncated=False, follow_redirects=True, deadline=None):  
    if payload: payload = urllib.urlencode(payload)
    if payload and method == GET: 
        url += "?" + payload
        payload = None
    logging.debug("Fetching %s with %s" % (url, payload))
    ret = urllib2.urlopen(url, payload)
    return URLFetchResponse(ret)
