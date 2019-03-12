from untils import Handler, SocketHandler
from tornado.httpclient import AsyncHTTPClient
import asyncio
from tornado.web import authenticated
import json
from untils import escapdict


class BaseHandler(Handler):

    def get_current_user(self):
        return self.get_secure_cookie('uid', None)


class BaseIndex(BaseHandler):
    __route__ = r'/login'

    async def get(self, *args, **kwargs):
        if self.get_current_user():
            self.redirect('/')
        self.render('login.html', name=None)

    async def post(self, *args, **kwargs):
        self.set_secure_cookie('uid', self.get_argument('Full Name'))
        self.redirect('/')


class EditConf(BaseHandler):
    __route__ = r'/conf/([\w\.]+)'

    async def get(self, *args, **kwargs):
        file = './conf.json'
        with open(file) as f:
            data = json.load(f)
        self.render('config.html', name=f.name, func=escapdict, contain=data)

    async def post(self, *args, **kwargs):
        data = self.request.arguments
        data.pop('_xsrf')
        name = data.pop('name')[0].decode('utf8')
        data = {k: v[0].decode('utf8') for k, v in data.items()}
        pass

    class Logout(BaseHandler):
        __route__ = r'/logout'

        async def get(self, *args, **kwargs):
            if (self.get_current_user()):
                self.clear_cookie("uid")
                self.redirect("/")

    class index(BaseHandler):
        __route__ = '/'

        @authenticated
        async def get(self, *args, **kwargs):
            self.render('index.html', name=self.get_secure_cookie('uid'))
