 # -*- coding: utf-8 -*-
import pymongo as pym
import json
import tornado.ioloop
from tornado.options import define, options
from tornado.web import Application, RequestHandler, HTTPError


class PoemHandler(RequestHandler):

    def initialize(self, db):
        self.db = db

    def get(self):
        query = self.get_argument('query')
        limit - self.get_argument('limit', 30)
        try:
            jquery = json.loads(query)
        except ValueError:
            raise HTTPError(400)

        cursor = self.db['ngrams'].find(jquery).limit(limit)

        res = []
        for doc in cursor:
            res.append(doc)

        self.write(json.dumps(res))

def main():
    define("host", default="127.0.0.1", help="Host IP")
    define("port", default=9090, help="Port")
    define("mongodb_url", default="127.0.0.1:27017", help="MongoDB connection URL")
    tornado.options.parse_command_line()

    # init database connection
    client = pym.MongoClient(options.mongodb_url)
    db = client['shalk']

    application = Application([(r"/ngrams/find", PoemHandler, dict(db=db)),])

    application.listen(options.port, options.host)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

