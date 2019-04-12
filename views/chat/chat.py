import json
import time
from hashlib import sha256
from weakref import WeakValueDictionary

import tornado.auth

from untils import Handler, SocketHandler

if not __debug__:
    __host__ = r'chat\.wufatiannv\.xyz'


class ChatManage(dict):
    # def __setitem__(self, key, value):
    #     if 'uid' not in key:
    #         raise RuntimeError('User Not have uid.')
    #     return super().__setitem__(key, value)
    async def broadcast(self, message, user=None):
        if user:
            for i, v in self.items():
                if i == user:
                    continue
                else:
                    wt = json.dumps(dict(user=v[0]['fn'], msg=message))
                    await v[1].write_message(wt)
        else:
            for i, v in self.items():
                wt = json.dumps(dict(user="Sys", msg=message))
                await v[1].write_message(wt)


cm = ChatManage()  # 类成员


class Login(Handler):
    if __debug__:
        __route__ = r'/chat/login'
    else:
        __route__ = r'/login'

    async def get(self, *args, **kwargs):
        user = self.get_secure_cookie('user-id', None)

        if user:
            self.redirect('/chatroom')
        else:
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
        self.application.db['chat'].insert(udict)
        self.set_secure_cookie('user-id', uid)

        cm[uid] = [udict, ]
        if __debug__:
            self.redirect('/chat/chatroom')
        else:
            self.redirect('/chatroom')


class ChatRoom(Handler):
    if __debug__:
        __route__ = r'/chat/chatroom'
        ws_addr = "ws://127.0.0.1:8000/ws/chat"
    else:
        __route__ = r'/chatroom'
        ws_addr = "ws://chat.wufatiannv.xyz/ws/chat"

    async def get(self, *args, **kwargs):
        user = self.get_secure_cookie('user-id', None)
        if user:
            if user not in cm:
                uinfo = self.application.db['chat'].find_one(
                    {'id': user.decode('utf8')})
                if uinfo:
                    uinfo.pop('_id')
                    cm[user] = [uinfo, ]
                    return self.render(
                        'chat.html', uid=uinfo['fn'], uinfo=uinfo, wsockaddr=self.ws_addr)
            else:
                uinfo = cm[user][0]
                return self.render(
                    'chat.html', uid=uinfo['fn'], uinfo=uinfo, wsockaddr=self.ws_addr)
        self.clear_all_cookies()
        if __debug__:
            self.redirect('/chat/login')
        else:
            self.redirect('/login')


class Chat(SocketHandler):
    __route__ = r'/ws/chat'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def check_origin(self, origin):
        return True

    async def open(self):
        db = self.application.db['chche']
        uid = self.get_secure_cookie('user-id')
        cm[uid].append(self)
        await cm.broadcast("Welecon {} Join Chat room.".format(cm[uid][0]['fn']))
        cache = list(db.find().sort('time', -1).limit(20))
        for i in cache[::-1]:
            await self.write_message({'user': i['fn'], 'msg': i['msg']})

    async def on_message(self, message):
        db = self.application.db['chche']
        uid = self.get_secure_cookie('user-id')
        db.insert(
            dict(time=time.time(), fn=cm[uid][0]['fn'], uid=uid, msg=message))
        await cm.broadcast(message, uid)

    def on_close(self):
        uid = self.get_secure_cookie('user-id')
        cm[uid].pop(-1)
