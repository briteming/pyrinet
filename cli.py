#!/usr/bin/env python

import json
from struct import pack, unpack
import socket
import ssl


class Client(object):
    def __init__(self, mgr_addr, keyfile, certfile):
        self.keyfile = keyfile
        self.certfile = certfile
        self.mgr_addr = mgr_addr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(mgr_addr)
        self.sock = ssl.wrap_socket(
            self.sock, keyfile=keyfile, certfile=certfile)

    def recv_msg(self):
        head = self.recv_n(2)
        if head is not None:
            size = unpack('H', head)[0]
            packet = self.recv_n(size)
            if packet is not None:
                try:
                    return json.loads(packet)
                except:
                    pass

    def recv_n(self, size):
        datas = []
        remain = size
        while remain > 0:
            data = self.sock.recv(remain)
            if not data:
                return
            datas.append(data)
            remain -= len(data)
        return ''.join(datas)

    def send_msg(self, msg):
        data = json.dumps(msg)
        self.sock.send(pack('H', len(data)) + data)

    def send(self, cmd, **args):
        args['cmd'] = cmd
        self.send_msg(args)

    def close(self):
        self.sock.close()

    def redirect(self, local, remote, protocol='tcp'):
        self.send('redirect', protocol=protocol, local=local, remote=remote)
        rep = self.recv_msg()
        return rep['ok']

    def list_redirect(self):
        self.send('list_redirect')
        return self.recv_msg()

    def drop_redirect(self, local, protocol='tcp'):
        self.send('drop_redirect', local=local, protocol=protocol)
        return self.recv_msg()['ok']

    def shutdown(self):
        self.send('shutdown')


if __name__ == '__main__':
    cli = Client(('127.0.0.1', 1234), keyfile='clikey.pem',
        certfile='clicert.pem')
    print cli.redirect(local='127.0.0.1:8080', remote='127.0.0.1:8000')
    print cli.list_redirect()
    cli.close()
