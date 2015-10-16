from tornado.httpclient import HTTPClient
import json
import random
import pymongo as pym
from cache import lru_cache

class Ngrams(object):
    """ This class is a database wrapper for the Ngrams queries. It has 2 run
    modes: server and client. The server actually has the connection for the
    database, and is responsible for doing the queries in an efficient way.
    This mode is run on the server hosted on `FIND_URL` and the results are
    returned through the web server.
    The client dont actually has the db connection, and it get the results by
    querying the server through HTTP POST's
    """

    FIND_URL = 'http://shalk-helderm.rhcloud.com/ngrams/find'

    def __init__(self, db=None):
        self.db = db
        self.cl = HTTPClient()

    def find(self, query, n, limit=0):
        q = json.dumps(query)
        return self._cached_find(q, n, limit)

    @lru_cache()
    def _cached_find(self, q, n, limit=0):

        query = json.loads(q)

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
