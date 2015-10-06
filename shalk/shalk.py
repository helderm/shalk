 # -*- coding: utf-8 -*-
import pymongo as pym
import json
import tornado.ioloop
from tornado.options import define, options
from tornado.web import Application, RequestHandler, HTTPError

from poem import Poem

class PoemHandler(RequestHandler):

    def initialize(self, db):
        self.db = db

    def get(self):
        pattern = ['*****', '*******', '*****']
        poem = Poem(pattern)

        self.write(poem.generate())

class NgramsHandler(RequestHandler):

    def initialize(self, db):
        self.db = db

    def post(self):
        body = json.loads(self.request.body)
        query = body['query']
        limit = body['limit']

        cursor = self.db['ngrams'].find(query, {'_id':0}).limit(limit)
        self.write(json.dumps(list(cursor)))

def main():
    define("host", default="127.0.0.1", help="Host IP")
    define("port", default=9090, help="Port")
    define("mongodb_url", default="127.0.0.1:27017", help="MongoDB connection URL")
    tornado.options.parse_command_line()

    # init database connection
    client = pym.MongoClient(options.mongodb_url)
    db = client['shalk']

    application = Application([(r"/ngrams/find", NgramsHandler, dict(db=db)),
                                (r"/poem/get", PoemHandler, dict(db=db))])

    application.listen(options.port, options.host)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

