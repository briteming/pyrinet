# -*- coding: utf-8 -*-
'''
    WebSSH.user.models
    ~~~~~~~~~~~~~~~~~~

    user models.

    :copyright: (c) 2012 by Du Jiong.
    :license: BSD, see LICENSE for more details.
'''


from webadm import BaseModel
from sqlalchemy import *
from M2Crypto.EVP import pbkdf2
import string
import random
random = random.SystemRandom()


salt_choices = string.printable[:-6].replace('$', '')


class User(BaseModel):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(16), unique=True, index=True)
    password = Column(String(128))
    join_time = Column(DateTime)
    is_actived = Column(Boolean)

    def set_password(self, password):
        salt = ''.join([random.choice(salt_choices) for _ in xrange(6)])
        digest = pbkdf2(password, salt, 10000, 32)
        digest = digest.encode('base64').replace('\n', '')
        self.password = '%s$%s' % (salt, digest)

    def check_password(self, password):
        if not self.password or '$' not in self.password:
            return False
        salt, digest = self.password.encode('utf8').split('$', 1)
        if isinstance(password, unicode):
            password = password.encode('utf8')
        d = pbkdf2(password, salt, 10000, 32)
        if d != digest.decode('base64'):
            return False
        return True
