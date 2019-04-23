import json
import time
from hashlib import sha256
from weakref import WeakValueDictionary

from tornado.web import authenticated

from untils import Handler, SocketHandler


if not __debug__:
    __host__ = r'chat\.wufatiannv\.xyz'


class BaseHandle(Handler):
    def get_login_url(self):
        if __debug__:
            __route__ = r'/chat/login'
        else:
            __route__ = r'/login'
        return __route__

    def get_current_user(self):
        uid = self.get_secure_cookie('user-id', None)
        if uid:
            uinfo = self.mondb['chat'].find_one(
                {'id': uid.decode('utf8')})
            if uinfo:
                uinfo.pop('_id')
                cm[uid] = [uinfo, ]
                return uid
            else:
                self.clear_cookie("user-id")
        return None

# class User:


class ChatManage(dict):
    # def __setitem__(self, key, value):
    #     if 'uid' not in key:
    #         raise RuntimeError('User Not have uid.')
    #     return super().__setitem__(key, value)
    # def add(self,id,*args):
    #     if id in self:

    def addUser(self, user, info):
        return self.__setitem__(user, [info, ])

    def addUserRaw(self, user, obj):
        item = self[user]
        if len(item) == 1:
            item.append(obj)
        else:
            item[1] = opj

    def getUserInfo(self, user):
        if user in self:
            return self[user][0]
        else:
            return None

    def getUserRaw(self, user):
        if user in self:
            return self[user][1]
        else:
            return None

    def delUser(self, user):
        self.pop(user)

    async def broadcast(self, message, user=None):
        if user:
            fn = self.getUserInfo('user')['fn']
            for i, v in self.items():
                if i == user:
                    continue
                else:
                    wt = json.dumps(dict(user=fn, msg=message))
                    await v[1].write_message(wt)
        else:
            wt = json.dumps(dict(user="Sys", msg=message))
            for i, v in self.items():
                await v[1].write_message(wt)


cm = ChatManage()  # 类成员


class Login(Handler):
    if __debug__:
        __route__ = r'/chat/login(.*)'
    else:
        __route__ = r'/login(.*)'
    # @authenticated

    async def get(self, *args, **kwargs):
        self.render('login.html')

    async def post(self, *args, **kwargs):
        def mhash(*args):
            d = sha256()
            for a in args:
                d.update(a.encode('utf8'))
            return d.hexdigest()

        fn = self.get_body_argument('Full Name')
        mail = self.get_body_argument('Email')
        sub = self.get_body_argument('Subject')
        Message = self.get_body_argument('Message')

        uid = mhash(fn, mail)
        udict = dict(id=uid, fn=fn, mail=mail, sub=sub, mes=Message)
        self.mondb['chat'].insert(udict)
        self.set_secure_cookie('user-id', uid)
        udict.pop('_id')
        cm.addUser(uid.encode('utf8'), udict)
        self.redirect(self.get_argument("next", "/"))


class ChatRoom(BaseHandle):
    if __debug__:
        __route__ = r'/chat/chatroom'
        ws_addr = "ws://127.0.0.1:8000/ws/chat"
    else:
        __route__ = r'/chatroom'
        ws_addr = "ws://chat.wufatiannv.xyz/ws/chat"

    @authenticated
    async def get(self, *args, **kwargs):
        uinfo = cm.getUserInfo(self.current_user)
        return self.render(
            'chat.html', uid=uinfo['fn'], uinfo=uinfo, wsockaddr=self.ws_addr)


class Chat(SocketHandler):
    __route__ = r'/ws/chat'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def check_origin(self, origin):
        return True

    async def open(self):
        db = self.mondb['chche']
        uid = self.get_secure_cookie('user-id')
        cm.addUserRaw(uid, self)
        await cm.broadcast("Welecon {} Join Chat room.".format(cm[uid][0]['fn']))
        cache = list(db.find().sort('time', -1).limit(20))
        for i in cache[::-1]:
            await self.write_message({'user': i['fn'], 'msg': i['msg']})

    async def on_message(self, message):
        db = self.mondb['chche']
        uid = self.get_secure_cookie('user-id')
        db.insert(
            dict(time=time.time(), fn=cm[uid][0]['fn'], uid=uid, msg=message))
        await cm.broadcast(message, uid)

    def on_close(self):
        uid = self.get_secure_cookie('user-id')
        cm.delUser(uid)
