from untils import SocketHandler, Handler
from hashlib import sha256
import json


if not __debug__:
    __host__ = r'chat\.wufatiannv\.xyz'


class ChatManage(dict):
    # def __setitem__(self, key, value):
    #     if 'uid' not in key:
    #         raise RuntimeError('User Not have uid.')
    #     return super().__setitem__(key, value)
    async def broadcast(self, message, user):
        for i, v in self.items():
            if i == user:
                continue
            else:
                wt = json.dumps(dict(user=ChatRoom.users[user], msg=message))
                await v.write_message(wt)


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
        self.application.db['chat'].insert(
            dict(id=uid, fn=fn, mail=mail, sub=sub, mes=Message))
        self.set_secure_cookie('user-id', uid)
        ChatRoom.users[uid] = fn
        if __debug__:
            self.redirect('/chat/chatroom')
        else:
            self.redirect('/chatroom')


class ChatRoom(Handler):
    if __debug__:
        __route__ = r'/chat/chatroom'
        ws_addr = "ws://127.0.0.1:8000/ws"
    else:
        __route__ = r'/chatroom'
        ws_addr = "ws://chat.wufatiannv.xyz/ws"

    users = dict(Sys="Sys")

    async def get(self, *args, **kwargs):
        user = self.get_secure_cookie('user-id', None)
        if user:
            uinfo = self.application.db['chat'].find_one(
                {'id': user.decode('utf8')})
            if uinfo:
                uinfo.pop('_id')
                if user not in self.users:
                    self.users[user] = uinfo['fn']
                self.render(
                    'chat.html', uid=uinfo['fn'], uinfo=uinfo, wsockaddr=self.ws_addr)
                return
        self.clear_all_cookies()
        if __debug__:
            self.redirect('/chat/login')
        else:
            self.redirect('/login')


class Chat(SocketHandler):
    __route__ = r'/ws'
    cm = ChatManage()  # 类成员

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def check_origin(self, origin):
        return True

    async def open(self):
        self.write_message('welcome')
        uid = self.get_secure_cookie('user-id')
        self.cm[uid] = self
        await self.cm.broadcast("Welecon {} Join Chat room.".format(self.application.db['chat'].find_one(
            {'id': uid.decode('utf8')})['fn']),"Sys")

    async def on_message(self, message):
        uid = self.get_secure_cookie('user-id')
        await self.cm.broadcast(message, uid)

    def on_close(self):
        uid = self.get_secure_cookie('user-id')
        self.cm.pop(uid)
