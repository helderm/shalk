from tornado.httpclient import HTTPClient
import json
from urllib import urlencode

class Ngrams(object):
    FIND_URL = 'http://shalk-helderm.rhcloud.com/ngrams/find'

    def __init__(self):
        self.cl = HTTPClient()

    def find(self, query, limit=30):
        body = { 'query': query,
                 'limit': limit }

        res = self.cl.fetch(Ngrams.FIND_URL, body=json.dumps(body), method='POST')
        return json.loads(res.body)

def main():
    ngrams = Ngrams()
    res = ngrams.find({'word1': 'horse'})
    print res

if __name__ == '__main__':
    main()
