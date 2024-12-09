from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "asdr3298509hkhko5490i52934t548/*/*84234wersd"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
CORS_ORIGIN_ALLOW_ALL = True

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "../db.sqlite3"),
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, "../static")
MEDIA_ROOT = os.path.join(BASE_DIR, "../media")

STATIC_URL = "/static/"
MEDIA_URL = "/media/"
MAUTIC_URL = "https://mautic.djnd.si/api/"

SALT = "something/stupid"

BASE_URL = "http://localhost:8888/"

SUPPORT_MAIL = "vsi@danesjenovdan.si"

FROM_MAIL = "postar@danesjenovdan.si"


MAUTIC_USER = "filip@danesjenovdan.si"
MAUTIC_PASS = "necakajpomladi"

MERCHANT_ID = "jr2yzbryywyqxk8r"
PUBLIC_KEY = "2rpxf3xmfzss33bc"
PRIVATE_KEY = "9ca476f068f01e469a2d4dbddd2bc257"

CEBELCA_KEY = "lcv1c4n5psdq35062h90e4asgh983rgrd1wiuecs"
SLACK_KEY = "xoxp-2166854968-16070161283-198810942659-c5e5888db47376f6ea7149b7dec701f7"

IBAN = "SI56 6100 0000 5740 710"
TO_NAME = "Danes je nov dan"
TO_ADDRESS1 = "Resljeva cesta 25"
TO_ADDRESS2 = "1000 Ljubljana"
EMAIL_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
