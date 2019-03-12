import asyncio
from tornado.web import Application, RequestHandler
from tornado.options import define, options
from untils import add_routers, logger
import tornado.httpserver
import tornado.ioloop
from pymongo.pool import Pool
import pymongo
import os

define("port", default=8000, help="run on the given port", type=int)


def init(app):
    add_routers(app, 'views')

    return app


class Applicationutils(Application):

    def __init__(self, handlers=None, default_host=None, transforms=None, **settings):
        super().__init__(handlers, default_host, transforms, **settings)
        self.db = pymongo.MongoClient(port=27017)['tornado']


if __name__ == '__main__':
    tornado.options.parse_command_line()
    setting = {
        "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
        "template_path": 'templates',
        "autoreload": True,
        "login_url": '/login',
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
    }
    app = Applicationutils(**setting)
    http_server = tornado.httpserver.HTTPServer(init(app))
    http_server.listen(options.port)
    logger.info("Start server http://127.0.0.1:{}".format(options.port))
    tornado.ioloop.IOLoop.current().start()
