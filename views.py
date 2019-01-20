from untils import Handler
from tornado.httpclient import AsyncHTTPClient
import tornado.gen


class IndexHandler(Handler):
    __route__ = '/'

    async def post(self):
        title = self.get_argument('title', "Daday")
        name = self.get_argument('name')
        await self.render('index_base.html', title=title, content=name)

    def get(self):
        self.render('index_base.html', title='Welcome', content="Welcome")


class FetchHandle(Handler):
    __route__ = r'/url=(.*)'

    async def get(self, url):
        req = AsyncHTTPClient()
        res = await req.fetch(url)
        self.render('base.html', content=res.body)
