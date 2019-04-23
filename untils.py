import logging
import os
import time
import types
from abc import ABC
from threading import Lock, Thread, current_thread
from typing import Awaitable, Optional

import redis
import tornado.web
import tornado.websocket

logging.basicConfig(level=logging.DEBUG, format='|'.join(
    ['%(levelname)7s', '%(filename)10s', '%(lineno)d', '%(threadName)s', '%(asctime)s', '%(message)s']))
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RouteMixIn:
    __host__ = None  # default virtual host.
    __route__ = None  # default route.

    @property
    def route(self):
        return self.__route__

    @property
    def mondb(self):
        return self.application.mdb

    @property
    def redb(self):
        return self.application.redis


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
    n = moudel_name.rfind(".")  # 寻找字符串中的.的位置
    if n == (-1):
        mod = __import__(moudel_name, globals(), locals())
    else:
        name = moudel_name[n + 1:]
        mod = getattr(__import__(
            moudel_name[:n], globals(), locals(), [name]), name)

    defaultHost = getattr(mod, "__host__", r".*")
    for attr in dir(mod):
        if attr.startswith('_'):
            continue
        attr = getattr(mod, attr)
        if not isinstance(attr, type) or not issubclass(attr, (Handler, SocketHandler)):
            continue
        host = getattr(attr, '__host__')
        if host == None:
            host = defaultHost
        route = getattr(attr, '__route__')
        if host and route:
            app.add_handlers(host_pattern=host, host_handlers=[(route, attr)])
            logger.info('Add route host:{} route:{} with {}'.format(
                host, route, attr))
        else:
            logger.debug("Not find route {} ".format(attr))


def setLogLevel(level: str) -> None:
    global logger
    level = getattr(logging, level, logging.INFO)
    logger.setLevel(level)


""" def lock(from_url, name, ex=10, slower=False):
    lock = Lock()
    redisObj = redis.from_url(from_url)
    assert redisObj.ping()
    uuid = str(os.getpid())+str(current_thread().ident)
    flag = True

    def addtime():
        while flag:
            ttl = redisObj.ttl(name)
            # print("续命", current_thread().name, ttl)
            if ttl < ex:
                redisObj.expire(name, ex)
            # elif ttl < ex:
            #     redisObj.expire(name, ex)

            time.sleep(ex-0.5)

    def deltx():
        script = "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end"
        redisObj.eval(script, 1, name, uuid)  # Lua脚本


    def decorde(func):
        def wrap(*args, **kwargs):
            while True:
                x=redisObj.eval("if redis.call('ttl',KEYS[1]) >0 then \
                                        return redis.call('ttl',KEYS[1])  \
                                    else \
                                        return redis.call('set',KEYS[1],ARGV[1],'EX',ARGV[2],'NX') \
                                    end",1,name,uuid,ex)
                if x==b'OK':
                    break
                else:
                    time.sleep(int(x))
            if slower:
                t = Thread(None, addtime)
                t.setDaemon(True)
                t.start()
            result = func(*args, **kwargs)
            nonlocal flag
            flag = False
            deltx()
            return result
        return wrap
    return decorde


@lock("redis://127.0.0.1:32768/0", "local",1, slower=True)
def func1():
    print("fun1 runing...")
    time.sleep(2)
    print("func1 done.")


@lock("redis://127.0.0.1:32768/0", "local")
def func2():
    print("fun2 runing...")
    time.sleep(3)
    print("func2 done.")

if __name__ == "__main__":
    import sys
    if sys.argv[1]=="1":
        func1()
    else:
        func2()

     """