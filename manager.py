#!/usr/bin/env python

import gevent
import json
from gevent import socket
from gevent.event import Event
from gevent.pool import Group
from gevent import ssl
from struct import pack, unpack
import argparse
import logging
from msg import Msg
from redirector import Redirector


class DataPig(object):
    def __init__(self):
        self.datas = []
        self.recved = 0
        self.size = None

    def feed(self, data):
        self.datas.append(data)
        self.recved += len(data)

        if self.size is None:
            if self.recved >= 2:
                datas = ''.join(self.datas)
                self.size = unpack('H', datas[:2])[0]
                assert self.size > 0
                self.datas = [datas[2:]]
                self.recved -= 2
            else:
                return
        return self.check_msg()

    def check_msg(self):
        if not self.size or self.recved < self.size:
            return

        datas = ''.join(self.datas) if len(self.datas) > 1 else self.datas[0]
        packet = datas[:self.size]
        self.datas = [datas[self.size:]]
        self.recved = self.recved - self.size
        self.size = None

        msg = json.loads(packet)
        if not isinstance(msg, dict) or 'cmd' not in msg:
            raise ValueError('invalid msg')
        return msg


class MgrShutdown(Exception):
    pass


class Manager(object):
    def __init__(self, config_addr, keyfile,
            certfile, cacerts, backlog=10):
        if isinstance(config_addr, basestring):
            ip, port = config_addr.split(':')
            config_addr = (ip, int(port))

        self.keyfile = keyfile
        self.certfile = certfile
        self.cacerts = cacerts
        self.config_addr = config_addr
        self.backlog = backlog
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.end_evt = Event()
        self.clients = Group()
        self.redirectors = {}
        self.msg_processors = {
            'redirect': self.m_redirect,
            'list_redirect': self.m_list_redirect,
            'drop_redirect': self.m_drop_redirect,
            'shutdown': self.m_shutdown,
        }

        logging.info('manager initialized')

    def run(self):
        logging.info('manager start to run')
        self.sock.bind(self.config_addr)
        logging.info('manager bind to: %s:%d' % self.config_addr)
        self.sock.listen(self.backlog)
        accept_let = gevent.spawn(self.accept_let)

        self.end_evt.wait()
        logging.info('shutdown evt recved')
        accept_let.kill()
        self.clients.kill()

    def accept_let(self):
        while True:
            sock, addr = self.sock.accept()
            try:
                sock = ssl.wrap_socket(sock, keyfile=self.keyfile,
                    certfile=self.certfile, server_side=True,
                    cert_reqs=ssl.CERT_REQUIRED, ca_certs=self.cacerts)
            except ssl.SSLError, e:
                print e
                continue
            self.clients.spawn(self.client_let, sock, addr)

    def client_let(self, sock, addr):
        pig = DataPig()
        while True:
            try:
                data = sock.recv(65535)
                if len(data) == 0:
                    logging.debug('client out')
                    break
                msg = pig.feed(data)
            except:
                logging.warn('client let error')
                break
            if msg is not None:
                try:
                    ret = self.on_msg(msg)
                except MgrShutdown:
                    self.end_evt.set()
                if ret is not None:
                    data = json.dumps(ret)
                    sock.send(pack('H', len(data)) + data)

    def on_msg(self, msg):
        msg = Msg.new_msg(msg)
        if msg is not None:
            processor = self.msg_processors.get(msg.cmd, None)
            if processor is not None:
                try:
                    return processor(msg)
                except MgrShutdown:
                    raise
                except Exception, e:
                    logging.error('exception: %r', e)
                    raise
        else:
            logging.warn('invalid msg')

    def m_redirect(self, msg):
        if msg.key not in self.redirectors:
            logging.info('redirect [%s]%s to %s' % (
                msg.protocol, msg.local, msg.remote))
            r = Redirector(msg)
            r.start()
            self.redirectors[msg.key] = r
            return {'ok': True}
        return {'ok': False}

    def m_list_redirect(self, msg):
        return map(lambda x: x.dump(), self.redirectors.values())

    def m_drop_redirect(self, msg):
        if msg.key in self.redirectors:
            self.redirectors.pop(msg.key).kill()
            return {'ok': True}
        return {'ok': False}

    def m_shutdown(self, msg):
        raise MgrShutdown


if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s %(levelname)s]: %(message)s',
        level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('-B', '--bind', help='address to bind', required=True)
    parser.add_argument('--backlog', help='backlog of manager socket',
        default=10, type=int)
    parser.add_argument('-K', '--keyfile', help='keyfile for SSL connection',
        default='mgrkey.pem')
    parser.add_argument('-C', '--certfile', help='certfile for SSL connection',
        default='mgrcert.pem')
    parser.add_argument('--cacerts', help='file of caacerts',
        default='cacerts.pem')
    args = parser.parse_args()

    mgr = Manager(args.bind, keyfile=args.keyfile,
        certfile=args.certfile, cacerts=args.cacerts, backlog=args.backlog)
    mgr.run()
