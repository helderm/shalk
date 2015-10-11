from tornado.httpclient import HTTPClient
import json
import random
import pymongo as pym

class Ngrams(object):
    FIND_URL = 'http://shalk-helderm.rhcloud.com/ngrams/find'

    def __init__(self, db=None):
        self.db = db
        self.cl = HTTPClient()

    def find(self, query, n, limit=0, randorder=True):

        #if randorder and 'rand' not in query:
        #    r = random.random()
        #    op = random.choice(['$lt','$gt'])
        #    query['rand'] = { op: r }

        # if we have a db connection, use it!
        if self.db:
            sortorder = random.choice([ pym.ASCENDING, pym.DESCENDING ])

            coll = 'n{0}grams'.format(n)
            cursor = self.db[coll].find(query, {'_id':0, 'rand': 0}).sort('rand', sortorder).limit(limit)
            return list(cursor)

        body = { 'query': query,
                 'n': n,
                 'limit': limit }

        res = self.cl.fetch(Ngrams.FIND_URL, body=json.dumps(body), method='POST', request_timeout=0.0)
        return json.loads(res.body)


def main():
    #client = pym.MongoClient()
    #db = client['shalk']
    #ngrams = Ngrams(db=db)

    ngrams = Ngrams()
    res = ngrams.find({'word1': 'music'})
    print res

if __name__ == '__main__':
    main()
