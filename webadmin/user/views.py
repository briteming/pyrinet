# -*- coding: utf-8 -*-
'''
    WebSSH.user.views
    ~~~~~~~~~~~~~~~~~

    user views.

    :copyright: (c) 2012 by Du Jiong.
    :license: BSD, see LICENSE for more details.
'''


from flask import *
from models import *
import forms


module = Blueprint('user', __name__)


@module.route('/login', methods=('GET', 'POST'))
def login():
    if request.user is not None:
        return redirect(url_for('home'))
    error = None
    if request.method == 'POST':
        form = forms.LoginForm(request.form)
        if form.validate():
            user = g.db.query(User).filter(
                User.username == form.username.data).first()
            if user is not None and user.check_password(form.password.data):
                session['user'] = user
                request.user = user
                return redirect(url_for('home'))
            else:
                error = 'username or password wrong!'
        print dir(form.username)
    else:
        form = forms.LoginForm()
    return render_template('user/login.html', form=form, error=error)


@module.route('/logout')
def logout():
    if request.user:
        request.user = None
        session.pop('user')
    return redirect(url_for('home'))
