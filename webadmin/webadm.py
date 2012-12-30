from flask import Flask, g, request, session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import sys


root_path = os.path.dirname(__file__)


def root_join(*segs):
    return os.path.join(root_path, *segs)
sys.path.append(root_path)
sys.path.append(root_join('..'))


app = Flask(__name__)
app.root_join = root_join
app.root_path = root_path
app.config.from_pyfile('config.py')
db_engine = create_engine(app.config['DATABASE'], convert_unicode=True)
Session = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)
BaseModel = declarative_base()


def objects(cls):
    return g.db.query(cls)
BaseModel.objects = classmethod(objects)


def objects_filter(cls, **filters):
    fs = []
    for k, v in filters.iteritems():
        if '__' in k:
            if k.endswith('__gt'):
                fs.append(getattr(cls, k[:-4]) > v)
            elif k.endswith('__lt'):
                fs.append(getattr(cls, k[:-4]) < v)
            elif k.endswith('__gte'):
                fs.append(getattr(cls, k[:-4]) >= v)
            elif k.endswith('__lte'):
                fs.append(getattr(cls, k[:-4]) <= v)
            else:
                fs.append(getattr(cls, k) == v)
        else:
            fs.append(getattr(cls, k) == v)
    return g.db.query(cls).filter(*fs)
BaseModel.filter = classmethod(objects_filter)


def objects_get(cls, **filters):
    return objects_filter(cls, **filters).first()
BaseModel.get = classmethod(objects_get)


@app.before_request
def before_request():
    g.db = Session()
    if 'user' in session:
        request.user = session['user']
    else:
        request.user = None


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


def find_modules(modules):
    if os.path.isfile(app.root_join('home.py')):
        __import__('home')
    if os.path.isfile(app.root_join('models.py')):
        __import__('models')
    for module in modules:
        if isinstance(module, tuple):
            module_name, url_prefix = module
        else:
            module_name = module
            url_prefix = '/' + module
        if os.path.isfile(app.root_join(module_name, 'models.py')):
            __import__('%s.models' % module_name)
        if os.path.isfile(app.root_join(module_name, 'views.py')):
            m = __import__('%s.views' % module_name)
            if hasattr(m.views, 'module'):
                app.register_blueprint(m.views.module, url_prefix=url_prefix)


find_modules(app.config['INSTALLED_MODULES'])


def get_client():
    from client import Client
    return Client(app.config['MANAGER_ADDR'], app.config['KEY_FILE'],
        app.config['CERT_FILE'])
app.get_client = get_client
