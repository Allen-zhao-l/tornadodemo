import asyncio
from tornado.web import Application, RequestHandler
from untils import add_routers, logger
import tornado.httpserver
import tornado.ioloop


def init(app):
    add_routers(app, 'views')

    return app


if __name__ == '__main__':
    app = Application(template_path='templates', autoreload=True)
    http_server = tornado.httpserver.HTTPServer(init(app))
    http_server.listen(8000)
    tornado.ioloop.IOLoop.current().start()
