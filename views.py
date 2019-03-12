from untils import Handler, SocketHandler
from tornado.httpclient import AsyncHTTPClient
import asyncio
from tornado.web import authenticated


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
