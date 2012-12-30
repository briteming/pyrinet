DEBUG = True
DATABASE = 'sqlite:///webadm.db'
SECRET_KEY = '\x8b\x89\xf2l(\xf0xcd\x05@\x9d'

INSTALLED_MODULES = (
    'user',
    'redirector',
    )

MANAGER_ADDR = ('127.0.0.1', 1234)
KEY_FILE = '../clikey.pem'
CERT_FILE = '../clicert.pem'
