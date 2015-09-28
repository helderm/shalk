# -*- coding: utf-8 -*-
import tornado.ioloop
from tornado.web import Application, RequestHandler
from tornado.options import define, options
import os
import pymongo as pym


class NgramsHandler(RequestHandler):

    def initialize(self, db):
        self.db = db

    def get(self):
        # optional query string arg
        freq = self.get_argument('freq', None)

        # required query string arg
        word0 = self.get_argument('word0')

        query = { 'word0': word0 }
        if freq:
            query['freq'] = freq

        # query the database
        ngram = self.db['ngrams'].find_one(query)

        self.write('ngrams = {0}'.format(ngram))


def main():
    define("host", default="127.0.0.1", help="Host IP")
    define("port", default=8080, help="Port")
    tornado.options.parse_command_line()

    # init database connection
    client = pym.MongoClient(os.getenv('OPENSHIFT_MONGODB_DB_URL'))
    db = client['shalk']

    application = Application([(r"/ngrams/find", NgramsHandler, dict(db=db)),])

    application.listen(options.port, options.host)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
