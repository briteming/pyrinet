#!/usr/bin/env python

from flask.ext.script import Manager
from webadm import app, Session

manager = Manager(app)


@manager.command
def syncdb():
    from webadm import BaseModel, db_engine
    BaseModel.metadata.create_all(bind=db_engine)


@manager.command
def createuser():
    import getpass
    from user.models import User

    db = Session()
    while True:
        name = raw_input('username:')
        if db.query(User).filter(User.username == name).count():
            print 'user exists'
        else:
            break
    pwd = getpass.getpass('password:')
    user = User(username=name)
    user.set_password(pwd)
    db.add(user)
    db.commit()


if __name__ == "__main__":
    manager.run()
