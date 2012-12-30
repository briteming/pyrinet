# -*- coding: utf-8 -*-
'''
    WebSSH.user
    ~~~~~~~~~~~

    user init.

    :copyright: (c) 2012 by Du Jiong.
    :license: BSD, see LICENSE for more details.
'''


from flask import request, redirect, url_for
from functools import wraps


def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not request.user:
            return redirect(url_for('user.login') + '?next=' + request.path)
        return f(*args, **kwargs)
    return wrapper
