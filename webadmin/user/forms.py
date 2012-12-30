# -*- coding: utf-8 -*-
'''
    WebSSH.user.forms
    ~~~~~~~~~~~~~~~~~

    user forms.

    :copyright: (c) 2012 by Du Jiong.
    :license: BSD, see LICENSE for more details.
'''


import wtforms as forms
v = forms.validators


class LoginForm(forms.Form):
    username = forms.TextField(
        'Username', [v.Length(min=2, max=16)])
    password = forms.PasswordField('Password', [v.Length(min=5, max=16)])
