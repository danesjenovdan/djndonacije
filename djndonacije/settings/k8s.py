"""
Django settings for djndonacije project.

Generated by 'django-admin startproject' using Django 2.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import braintree

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = dict(
    SECRET_KEY=os.getenv('DJANGO_SECRET_KEY', 'r^&^$8c*g$6db1s!s7uk9c!v%*ps)_0)h$!f3m7$%(o4b+5qwk'),
    DEBUG=os.getenv('DJANGO_DEBUG', True),
    DATABASE_HOST=os.getenv('DJANGO_DATABASE_HOST', 'localhost'),
    DATABASE_PORT=os.getenv('DJANGO_DATABASE_PORT', '5432'),
    DATABASE_NAME=os.getenv('DJANGO_DATABASE_NAME', 'donacije'),
    DATABASE_USER=os.getenv('DJANGO_DATABASE_USER', 'postgres'),
    DATABASE_PASSWORD=os.getenv('DJANGO_DATABASE_PASSWORD', 'postgres'),
    STATIC_ROOT=os.getenv('DJANGO_STATIC_ROOT', os.path.join(BASE_DIR, '../static')),
    STATIC_URL=os.getenv('DJANGO_STATIC_URL_BASE', '/static/'),
    MEDIA_ROOT=os.getenv('DJANGO_MEDIA_ROOT', '/media/'),
    MEDIA_URL=os.getenv('DJANGO_MEDIA_URL_BASE', '/media/'),
    SOLR_URL=os.getenv('PARLAMETER_SOLR_URL', ''),
    MAUTIC_URL=os.getenv('MAUTIC_URL', ''),
    MAUTIC_USER=os.getenv('MAUTIC_USER', ''),
    MAUTIC_PASSWORD=os.getenv('MAUTIC_PASSWORD', ''),
    BRAINTREE_ENV=os.getenv('BRAINTREE_ENV', 'Sandbox'),
    BRAINTREE_MERCHANT_ID=os.getenv('BRAINTREE_MERCHANT_ID', ''),
    BRAINTREE_PUBLIC_KEY=os.getenv('BRAINTREE_PUBLIC_KEY', ''),
    BRAINTREE_PRIVATE_KEY=os.getenv('BRAINTREE_PRIVATE_KEY', ''),
    SALT=os.getenv('SALT', ''),
    DJANGO_BASE_URL=os.getenv('DJANGO_BASE_URL', 'http://localhost:8000'),
    IBAN=os.getenv('DJANGO_BASE_URL', 'SI56 6100 0000 5740 710'),
    TO_NAME=os.getenv('DJND_IBAN', 'Danes je nov dan'),
    TO_ADDRESS1=os.getenv('DJND_UPN_TO_ADDRESS1', 'Parmova 20'),
    TO_ADDRESS2=os.getenv('DJND_UPN_TO_ADDRESS2', '1000 Ljubljana'),
    EMAIL_TOKEN=os.getenv('EMAIL_TOKEN', ''),
    AGRUM_TOKEN=os.getenv('AGRUM_TOKEN', ''),
)

ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env['SECRET_KEY']
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env['DEBUG']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': env['DATABASE_HOST'],
        'PORT': env['DATABASE_PORT'],
        'NAME': env['DATABASE_NAME'],
        'USER': env['DATABASE_USER'],
        'PASSWORD': env['DATABASE_PASSWORD'],
    }
}

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # installed libraries
    'adminsortable2',
    'rest_framework',
    'behaviors.apps.BehaviorsConfig',
    'corsheaders',
    'wkhtmltopdf',
    'tinymce',
    'import_export',
    # apps
    'djnd_supporters',
    'shop'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'djndonacije.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'djndonacije.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# static files for development
#STATIC_URL = '/static/'
STATIC_ROOT = env['STATIC_ROOT']

# static files for production
STATIC_URL = env['STATIC_URL']

MEDIA_ROOT = env['MEDIA_ROOT']
MEDIA_URL = env['MEDIA_URL']



SALT = env['SALT']
BASE_URL = env['DJANGO_BASE_URL']

# mautic credentials
MAUTIC_USER = env['MAUTIC_USER']
MAUTIC_PASS = env['MAUTIC_PASSWORD']

# third party services
CEBELCA_KEY = ""
SLACK_KEY = ""

IBAN = env['IBAN']
TO_NAME = env['TO_NAME']
TO_ADDRESS1 = env['TO_ADDRESS1']
TO_ADDRESS2 = env['TO_ADDRESS2']
EMAIL_TOKEN = env['EMAIL_TOKEN']
AGRUM_TOKEN = env['AGRUM_TOKEN']



GATEWAY = braintree.BraintreeGateway(
  braintree.Configuration(
    environment=getattr(braintree.Environment, env['BRAINTREE_ENV']),
    merchant_id=env['BRAINTREE_MERCHANT_ID'],
    public_key=env['BRAINTREE_PUBLIC_KEY'],
    private_key=env['BRAINTREE_PRIVATE_KEY']
  )
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'djnd_supporters.authentication.SubscriberAuthentication',
    ),
    #'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema'
}

THUMB_SIZE = (50, 50)

UPLOAD_IMAGE_URL = ''

DEFAULT_AUTO_FIELD='django.db.models.AutoField'

WKHTMLTOPDF_CMD_OPTIONS = {
    'quiet': False,
}

WKHTMLTOPDF_CMD = 'xvfb-run -a wkhtmltopdf'

if sentry_url := os.getenv('DJANGO_SENTRY_URL', False):
    # imports should only happen if necessary
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        sentry_url,
        integrations=[DjangoIntegration()],

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=0.1,
        send_default_pii=True,
    )

# TODO deprecate this objects
MAIL_TEMPLATES = {
    'EDIT_SUBSCRIPTIPNS': 1,
    'WELLCOME_MAIL': 2,
    'SHOP_THANKSGIVING_UPN': 6,

    'DONATION_WITH_GIFT': 40,
    'DONATION_WITHOUT_GIFT': 40,

    'DONATION_WITH_GIFT_UPN': 240,
    'DONATION_WITHOUT_GIFT_UPN': 240,

    # donation gifts
    'GIFT_SENT': 26,
    'GIFT_WITH_GIFT': 27,
    'GIFT_WITHOUT_GIFT': 4,

    'CUSTOM_GIFT': 24,
    # or?
    'GIFT': 15, # done
    'SHOP_BT_PP' :289,
    'SHOP_UPN': 288,

    # parlameter tempaltes
    'PARLAMETER_UPN': 325,
    'PARLAMETER_SI': 322,
    'PARLAMETER_HR': 323,
    'PARLAMETER_BA': 324,
}

SEGMENTS = {
    'agrument': 1,
    'mesecne-novice-nov-segment': 12,
    'general': 2,
    'parlameter': 3,
    'donations': 4,
    'huda-pobuda': 17,
    'obljuba-dela-dolg': 18,
    'newsgradient': 19,
    'stanovanja-najemniski-sos': 20,
    'huda-pobuda-pusca-na-pomoc': 23,
    'huda-pobuda-glas-skupnosti': 24,
    'huda-pobuda-zapisimo-spomine': 25,
    'pravna-mreza': 26,
    'glas-ljudstva': 27,
}
EDIT_SUBSCRIPTIPNS_TEMPLATES = {
    18: 557,
    19: 732,
    20: 642,
    23: 767,
    24: 780,
    25: 781,
    26: 864,
}
