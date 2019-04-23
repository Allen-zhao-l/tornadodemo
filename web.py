import asyncio
import os

import pymongo
import redis
import tornado.httpserver
import tornado.ioloop
from pymongo.pool import Pool
from tornado.options import define, options
from tornado.web import Application, RequestHandler

from untils import add_routers, logger, setLogLevel

define("port", default=8000, help="run on the given port", type=int)
define("log_level",default="INFO",help="App log level",type=str)
define("debug",default=False,type=bool)


def init(app):
    setLogLevel(options.log_level)
    add_routers(app, 'views.views')
    add_routers(app, 'views.blog.blog')
    add_routers(app, 'views.chat.chat')
    add_routers(app, 'views.chat.api')
    return app

class Applicationutils(Application):
    def __init__(self, handlers=None, default_host=None, transforms=None, **settings):
        super().__init__(handlers, default_host, transforms, **settings)
        self.mdb = pymongo.MongoClient(port=27017)['tornado']
        self.redis=redis.Redis()
if __name__ == '__main__':
    tornado.options.parse_command_line()
    setting = {
        "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
        "template_path": 'templates',
        "autoreload": True,
        "login_url": '/login',
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "debug":options.debug
    }
    app = Applicationutils(**setting)
    http_server = tornado.httpserver.HTTPServer(init(app))
    lsaddr="127.0.0.1" if __debug__ else "172.17.0.1"
    http_server.listen(options.port)
    logger.info("Start server http://{}:{}".format(lsaddr,options.port))
    tornado.ioloop.IOLoop.current().start()
