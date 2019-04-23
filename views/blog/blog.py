from untils import Handler
import markdown


class Blog(Handler):
    __route__ = r'/blog'

    async def get(self, *args, **kwagrs):
        content = markdown.markdown("a", output_format="html")
        self.write(content)


class BlogSingle(Handler):
    __route__ = r'/blog-single'

    async def get(self, *args, **kwagrs):
        self.render('blog-single.html')
