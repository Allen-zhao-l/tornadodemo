from untils import Handler


class Blog(Handler):
    __route__ = r'/blog'

    async def get(self, *args, **kwagrs):
        self.render('blog.html')


class BlogSingle(Handler):
    __route__ = r'/blog-single'

    async def get(self, *args, **kwagrs):
        self.render('blog-single.html')
