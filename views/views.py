import asyncio
import json

import tornado.gen
from tornado.gen import coroutine
from tornado.httpclient import AsyncHTTPClient
from tornado.web import authenticated

from untils import Handler

class Home(Handler):
    __route__=r'(/|/index)'
    async def get(self,*args,**kwargs):
        self.render('index.html')

class Aboud(Handler):
    __route__=r'/about-me'
    async def get(self,*args,**kwargs):
        self.render('about-us.html')

