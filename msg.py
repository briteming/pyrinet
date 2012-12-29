import re
from gevent import socket


class MsgMeta(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, '_msgs'):
            cls._msgs = {}
        else:
            cmd = attrs['cmd']
            if cmd is not None:
                if cmd in cls._msgs:
                    raise TypeError('duplicated cmd: `%s`' % repr(cmd))
                cls._msgs[cmd] = cls
            if 'keys' not in attrs:
                raise TypeError('class %s missing `keys`' % name)
        super(MsgMeta, cls).__init__(name, bases, attrs)


class MsgError(Exception):
    pass


class Msg(object):
    __metaclass__ = MsgMeta

    def __init__(self, msg):
        for key in self.keys:
            if key not in msg:
                raise MsgError('missing key: `%s`' % key)
            cln = 'clean_' + key
            val = msg[key]
            if hasattr(self, cln):
                val = getattr(self, cln)(val)
            setattr(self, key, val)
        self.cmd = msg['cmd']
        self.msg = msg

    def __getattr__(self, key):
        return self.msg.get(key, None)

    @classmethod
    def new_msg(cls, msg):
        m_cls = cls._msgs.get(msg['cmd'], None)
        if m_cls is not None:
            try:
                return m_cls(msg)
            except OSError:
                pass

    def __str__(self):
        return repr(self.msg)


class RedirectMsg(Msg):
    cmd = 'redirect'
    keys = ('local', 'remote', 'protocol')
    addr_re = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$')

    def clean_local(self, data):
        if not self.addr_re.match(data):
            raise MsgError
        ip, port = data.split(':')
        return ip, int(port)

    def clean_remote(self, data):
        if not self.addr_re.match(data):
            raise MsgError
        ip, port = data.split(':')
        return ip, int(port)

    def clean_protocol(self, data):
        if data == 'tcp':
            self.sock_type = socket.SOCK_STREAM
        elif data == 'udp':
            self.sock_type = socket.SOCK_DGRAM
        else:
            raise MsgError
        return data

    @property
    def key(self):
        if not hasattr(self, '_key'):
            self._key = '%s:%s:%d' % (
                self.protocol, self.local[0], self.local[1])
        return self._key


class DropRedirect(RedirectMsg):
    cmd = 'drop_redirect'
    keys = ('protocol', 'local')


class ListRedirect(Msg):
    cmd = 'list_redirect'
    keys = ()


class Shutdown(Msg):
    cmd = 'shutdown'
    keys = ()
