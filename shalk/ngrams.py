from tornado.httpclient import HTTPClient
import json
import random
import pymongo as pym

class Ngrams(object):
    FIND_URL = 'http://shalk-helderm.rhcloud.com/ngrams/find'

    def __init__(self, db=None):
        self.db = db
        self.cl = HTTPClient()

    def find(self, query, limit=30, randorder=True):

        if randorder and 'rand' not in query:
            r = random.random()
            op = '$lt' if r > 0.5 else '$gt'
            query['rand'] = { op: r }

        # if we have a db connection, use it!
        if self.db:
            sortorder = random.choice([ pym.ASCENDING, pym.DESCENDING ])
            cursor = self.db['ngrams'].find(query, {'_id':0}, ).limit(limit).sort('rand', sortorder)
            return list(cursor)

        body = { 'query': query,
                 'limit': limit }

        res = self.cl.fetch(Ngrams.FIND_URL, body=json.dumps(body), method='POST')
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
