from abc import ABC
import logging
import types
from typing import Optional, Awaitable
import tornado.web
import tornado.websocket

logging.basicConfig(level=logging.DEBUG, format=
'|'.join(['%(levelname)7s', '%(filename)10s', '%(lineno)d', '%(threadName)s', '%(asctime)s', '%(message)s']))
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class RouteMixIn:
    __host__ = r'.*'  # default virtual host.
    __route__ = None  # default route.

    @property
    def route(self):
        return self.__route__


class SocketHandler(RouteMixIn, tornado.websocket.WebSocketHandler):
    pass


class Handler(RouteMixIn, tornado.web.RequestHandler):
    pass


def escapdict(d, pri=1):
    assert isinstance(d, dict)
    for k, v in d.items():
        if isinstance(v, dict):
            yield from escapdict(v, pri + 1)
        elif isinstance(v, (list, tuple)):
            for x in v:
                yield from escapdict(x, pri + 1)
        else:
            yield (pri, k, v)


def add_routers(app, moudel_name=None):
    logger.info("Start add routes...")
    n = moudel_name.rfind(".")  # 寻找字符串中的.的位置
    if n == (-1):
        mod = __import__(moudel_name, globals(), locals())
    else:
        name = moudel_name[n + 1:]
        mod = getattr(__import__(moudel_name[:n], globals(), locals(), [name]), name)
    for attr in dir(mod):
        if attr.startswith('_'):
            continue
        attr = getattr(mod, attr)
        if not isinstance(attr, type) or not issubclass(attr, Handler):
            continue
        host = getattr(attr, '__host__')
        route = getattr(attr, '__route__')
        if host and route:
            app.add_handlers(host_pattern=host, host_handlers=[(route, attr)])
            logger.info('Add route host:{} route:{} with {}'.format(host, route, attr))
        else:
            logger.warning("Not find route {} ".format(attr))
    logger.info("Add routes Done")
