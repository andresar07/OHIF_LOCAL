"""
Django settings for Annotations_back project.

Generated by 'django-admin startproject' using Django 3.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
from datetime import datetime
from time import gmtime, strftime

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-k!px*ib&+w8d@lnx0hb^g@tv_=t_&m!&5oijz4ui!60m1(%h%#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_yasg',
    'Annotations_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'Annotations_app.auth.middleware.googleauthmiddleware.GoogleAuthMiddleware',
    # 'Annotations_app.auth.middleware.authmiddleware.AuthMiddleware',
]

ROOT_URLCONF = 'Annotations_back.urls'

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

WSGI_APPLICATION = 'Annotations_back.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME', 'annotationsdb'),
        'USER': os.getenv('DB_USERNAME', 'imexhs'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'imexhs2023'),
        'HOST': os.getenv('DB_HOSTNAME', 'localhost'),
        'PORT': os.getenv('DB_PORT', 5432)
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#! SECURITY WARNING: don't use this  environment variable in production
TESTING = os.getenv('TESTING', 'False').lower() == 'true' 

# Variable environment multi tenant

TENANT_BASE_URL = os.getenv('TENANT_BASE_URL', 'http://localhost:8002')

# * tenant resources
USER_CUSTOM_RESOURCES = os.getenv('USER_CUSTOM_RESOURCES', 'False') == 'True'
if USER_CUSTOM_RESOURCES:
    resources =  os.getenv('TENANT_RESOURCES', 'DBANNOT_C001_01_TEST, annotations_db2').split(",")
    TENANT_RESOURCES = [s.strip() for s in resources]
else:
    TENANT_RESOURCES = []

# update resources on application start
UPDATE_RES_ON_START = os.getenv('UPDATE_RES_ON_START', 'False') == 'True'

# chek authorization token
JWT_AUTH_ENABLED = os.getenv('JWT_AUTH_ENABLED', 'False') == 'True'
# token source: header or cookie
JWT_TOKEN_SOURCE = os.getenv('JWT_TOKEN_SOURCE', 'cookie:GOOGLE_TOKEN_AQUILA')

# only accepts request from registered tenants
ONLY_REG_TENANTS_REQUESTS = os.getenv('ONLY_REG_TENANTS_REQUESTS', 'False') == 'True'

# Type of resource for this module back-end
RESOURCE_TYPE = os.getenv('RESOURCE_TYPE', 'annotationdb')

# lewvels -> DEBUG INFO WARNING ERROR CRITICAL
DJANGO_LOG_LEVEL = os.getenv('DJANGO_LOG_LEVEL', 'DEBUG')
DJANGO_LOG_FILE = os.getenv('DJANGO_LOG_FILE', 'logs.log.jsonl')

# v2
LOGGING = {
    'version': 1,
    # The version number of our log
    'disable_existing_loggers': False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s | %(levelname)s | %(message)s",
            "datefmt": strftime("%Y-%m-%d %H:%M:%S +0000", gmtime()),
            "encoding": 'utf-8',
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(message)s",
            "datefmt": strftime("%Y-%m-%d %H:%M:%S +0000", gmtime()),
        }
    },
    'handlers': {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        'file': {
            'level': DJANGO_LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            "formatter": "json",
            'filename': BASE_DIR / DJANGO_LOG_FILE,
            "backupCount": 5,
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
        },
    },
    'loggers': {
       "": {
            "handlers": ["console", "file"],
            "level": DJANGO_LOG_LEVEL,
            "propagate": True,
        },
    },
}
# Name of tenat id variable
NAME_VARIABLE_TENANT_GOOGLE = os.getenv('NAME_VARIABLE_TENANT_GOOGLE', 'tenant')

# time to update resources 
RESOURCES_REFRESH_TIME = int( os.getenv('RESOURCES_REFRESH_TIME', 0) )