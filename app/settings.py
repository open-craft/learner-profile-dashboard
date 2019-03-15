"""
Django settings for lti_lpd project.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

import nltk
from sklearn.externals import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_lti_tool_provider',
    'ordered_model',
    'app',
    'iframe',
    'lpd',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'iframe.middleware.iframe_middleware.IFrameFixMiddleware',
)

ROOT_URLCONF = 'app.urls'

WSGI_APPLICATION = 'app.wsgi.application'

# Session cookie: use a different name from edx
SESSION_COOKIE_NAME = 'lti-lpd'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

# Note: Override with a real database (e.g. mysql) in local_settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'lpd.sqlite'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.csrf',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

LOGIN_URL = 'admin:login'

# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'timestamp_formatter': {
            'format': '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        }
    },
    'handlers': {
        'stream_info_log': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'timestamp_formatter',
        },
        'file_debug_log_default': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'timestamp_formatter',
            'filename': os.path.join(BASE_DIR, 'default.log'),
        },
        'file_debug_log_security': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'timestamp_formatter',
            'filename': os.path.join(BASE_DIR, 'security.log'),
        },
        'file_debug_log_test': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'timestamp_formatter',
            'filename': os.path.join(BASE_DIR, 'test.log'),
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['stream_info_log'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['stream_info_log'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.template': {
            'handlers': ['stream_info_log'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['file_debug_log_security'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django_lti_tool_provider.views': {
            'handlers': ['file_debug_log_default'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'lpd.views': {
            'handlers': ['file_debug_log_default'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'lpd.client': {
            'handlers': ['file_debug_log_default'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'lpd.tests': {
            'handlers': ['file_debug_log_test'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Sensitive settings
# These are sensitive settings, and should be overridden in local_settings.py
SECRET_KEY = os.environ.get('SECRET_KEY', 'SET-ME')

# LTI settings
LTI_HOME_PAGE = 'lpd:home'
LTI_CLIENT_KEY = os.environ.get('LTI_CLIENT_KEY', 'SET-ME')
LTI_CLIENT_SECRET = os.environ.get('LTI_CLIENT_SECRET', 'SET-ME')

# Used to automatically generate stable passwords from anonymous user IDs coming from LTI requests.
# If compromised, attackers would be able to restore any student's password knowing their anonymous user ID from LMS.
PASSWORD_GENERATOR_NONCE = os.environ.get('PASSWORD_GENERATOR_NONCE', 'SET-ME')

# LDA model settings for the data analysis of qualitative answers - should be overwritten in local_settings.py
GROUP_KCS = ['kc_id_1_set-me', 'kc_id_2_set-me']

# Make sure you provided your LDA_MODEL and TFIDF_VECTORIZER files.
LDA_MODEL = joblib.load(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lda.pkl')
)
TFIDF_VECTORIZER = joblib.load(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'tfidf_vectorizer.pkl'
    )
)

# Make sure that 'punkt' tokenizer is downloaded
# (it's required to preprocess data for LDA model)
nltk.download('punkt')

# Adaptive Engine settings

# Domain of the Open edX instance that this LPD deployment is connected to
OPENEDX_INSTANCE_DOMAIN = os.environ.get('OPENEDX_INSTANCE_DOMAIN', 'SET-ME')
# URL of the Adaptive Engine deployment that this LPD deployment is connected to
ADAPTIVE_ENGINE_URL = os.environ.get('ADAPTIVE_ENGINE_URL', 'SET-ME')
# Auth token for requests to Adaptive Engine deployment that this LPD deployment is connected to
ADAPTIVE_ENGINE_TOKEN = os.environ.get('ADAPTIVE_ENGINE_TOKEN', 'SET-ME')

# pylint: disable=wildcard-import
try:
    from .local_settings import *  # NOQA
except ImportError:
    import warnings
    warnings.warn(
        'File local_settings.py not found.  You probably want to add it -- see README.md.'
    )
