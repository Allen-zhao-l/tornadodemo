from views.chat.chat import cm,BaseHandle
from tornado.web import authenticated
import json

if not __debug__:
    __host__ = r'chat\.wufatiannv\.xyz'
        
class CurUser(BaseHandle):
    if __debug__:
        __route__=r'/api/chat/currentuser'
    else:
        __route__=r'/api/currentuser'
    @authenticated
    async def get(self,*args,**kwargs):
        # print({k.decode('utf8'):v for k,v in cm.items()})
        self.write({k.decode('utf8'):v[0] for k,v in cm.items()})  