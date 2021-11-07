"""
Django settings for djndonacije project.

Generated by 'django-admin startproject' using Django 2.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'djnd_supporters.authentication.SubscriberAuthentication',
    ),
    #'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema'
}

THUMB_SIZE = (50, 50)

UPLOAD_IMAGE_URL = 'https://danesjenovdan.si/doniraj/hvala?token='

DEFAULT_AUTO_FIELD='django.db.models.AutoField'

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
