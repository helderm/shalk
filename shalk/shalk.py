# -*- coding: utf-8 -*-
import tornado.ioloop
from tornado.web import Application, RequestHandler
from tornado.options import define, options



class NgramsHandler(RequestHandler):
    def get(self):
        freq = self.get_argument('freq', None)
        word0 = self.get_argument('word0')

        self.write('freq = {0}, word0 = {1}'.format(freq, word0))


def main():
    define("host", default="127.0.0.1", help="Host IP")
    define("port", default=8080, help="Port")
    tornado.options.parse_command_line()

    application = Application([(r"/ngrams/find", NgramsHandler),])

    application.listen(options.port, options.host)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
