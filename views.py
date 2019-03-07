from untils import Handler


class index(Handler):
    __route__ = '/'

    async def get(self, *args, **kwargs):
        self.render('index_base.html', title='你好', content=self.request.remote_ip)


class T(Handler):
    pass
