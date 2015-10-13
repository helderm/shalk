from tornado.httpclient import HTTPClient
import json
import random
import pymongo as pym

class Ngrams(object):
    FIND_URL = 'http://shalk-helderm.rhcloud.com/ngrams/find'

    def __init__(self, db=None):
        self.db = db
        self.cl = HTTPClient()

    def find(self, query, n, limit=0):

        # if we have a db connection, use it!
        if self.db:
            sortorder = random.choice([ pym.ASCENDING, pym.DESCENDING ])

            coll = 'n{0}grams'.format(n)
            cursor = self.db[coll].find(query, {'_id':0, 'rand': 0, 'type': 0, 'syllables': 0}).sort('rand', sortorder).limit(limit)
            return list(cursor)

        # if not, query the server
        body = { 'query': query,
                 'n': n,
                 'limit': limit }

        res = self.cl.fetch(Ngrams.FIND_URL, body=json.dumps(body), method='POST', request_timeout=0.0)
        ret = json.loads(res.body)
        return ret

def main():
    ngrams = Ngrams()
    res = ngrams.find({'word1': 'music'})
    print res

if __name__ == '__main__':
    main()
