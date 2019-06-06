from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'asdr3298509hkhko5490i52934t548/*/*84234wersd'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
CORS_ORIGIN_ALLOW_ALL = True

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, '../db.sqlite3'),
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATIC_URL = '/static/'
MAUTIC_URL = 'http://mautic.server.com/api/'

SALT = 'something/stupid'

BASE_URL = 'http://localhost:8888/'

SUPPORT_MAIL = 'suport@server.com'

FROM_MAIL = 'info@server.com'


MAUTIC_USER = 'info@server.com'
MAUTIC_PASS = '1234'

MERCHANT_ID = "jr2yzbryywyqxk8r"
PUBLIC_KEY = "2rpxf3xmfzss33bc"
PRIVATE_KEY = "9ca476f068f01e469a2d4dbddd2bc257"

CEBELCA_KEY = "asdasdasdasdasd"
SLACK_KEY = "xoxp-asdasdasdasd-asdasdasdasd-asdasdasdasd-asdasdasdasdasdasdasdasd"

IBAN = 'SI56 1111 2222 3333 123'
TO_NAME = '123'
TO_ADDRESS1 = 'Address 20'
TO_ADDRESS2 = '1000 City'