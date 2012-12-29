from gevent.pool import Group
from gevent import Greenlet
from gevent import socket
from gevent.select import select


class LinkBroken(Exception):
    pass


class Linker(Greenlet):
    def __init__(self, remote, sock_type, sock):
        self.sock = sock
        self.sock.setblocking(0)
        self.remote = remote
        self.r_sock = socket.socket(socket.AF_INET, sock_type)
        self.r_sock.setblocking(0)
        self.writes, self.r_writes = [], []
        super(Linker, self).__init__()

    def _run(self):
        self.r_sock.settimeout(3)
        try:
            self.r_sock.connect(self.remote)
        except:
            return self.sock.close()

        while True:
            wset = []
            if self.writes:
                wset.append(self.sock)
            if self.r_writes:
                wset.append(self.r_sock)
            ifds, wfds, efds = select([self.sock, self.r_sock],
                wset, [self.sock, self.r_sock])

            try:
                self.on_read(ifds)
                self.on_write(wfds)
            except LinkBroken:
                self.close()
                break
            if efds:
                self.close()
                break

    def on_read(self, fds):
        for fd in fds:
            if fd == self.sock:
                data = self.sock.recv(65535)
                if not data:
                    raise LinkBroken
                self.r_writes.append(data)
                self.r_write()
            elif fd == self.r_sock:
                data = self.r_sock.recv(65535)
                if not data:
                    raise LinkBroken
                self.writes.append(data)
                self.write()

    def on_write(self, fds):
        for fd in fds:
            if fd == self.sock:
                self.write()
            elif fd == self.r_sock:
                self.r_write()

    def write(self):
        if self.writes:
            data = ''.join(self.writes)
            size = self.sock.send(data)
            if size == len(data):
                self.writes = []
            else:
                self.writes = [data[size:]]

    def r_write(self):
        if self.r_writes:
            data = ''.join(self.r_writes)
            size = self.r_sock.send(data)
            if size == len(data):
                self.r_writes = []
            else:
                self.r_writes = [data[size:]]

    def close(self):
        super(Linker, self).kill()
        self.sock.close()
        self.r_sock.close()


class Redirector(Greenlet):
    def __init__(self, msg):
        self.sock_type = msg.sock_type
        self.info = msg
        self.sock = socket.socket(socket.AF_INET, self.sock_type)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.links = Group()
        super(Redirector, self).__init__()

    def _run(self):
        self.sock.bind(self.info.local)
        self.sock.listen(64)

        while True:
            cli, addr = self.sock.accept()
            self.links.start(Linker(self.info.remote, self.sock_type, cli))

    def kill(self):
        self.links.kill()
        super(Redirector, self).kill()
        self.sock.close()

    def dump(self):
        return dict(protocol=self.info.protocol,
            local='%s:%d' % self.info.local,
            remote='%s:%d' % self.info.remote)
