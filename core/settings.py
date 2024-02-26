# -*- encoding: utf-8 -*-

# Libraries
import os
from datetime import timedelta

from unipath import Path
from dj_database_url import parse as db_url
from .utils import get_config, to_list
from anomaly_detection.constants import number_of_days, batch_minutes

# Build paths inside the project like this:
# BASE_DIR.parent to dive in
# BASE_DIR.child to reach one level above
BASE_DIR = Path(__file__).parent.parent
CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_config('SECRET_KEY', 'DEFAULT_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_config('DEBUG', 'True', cast=bool)

# Format of allowed hosts --> at least '127.0.0.1, .localhost' in .env file
# add additional hosts as comma separated in the same string
# load  settings from production server from .env
ALLOWED_HOSTS = get_config(
    'ALLOWED_HOSTS', '127.0.0.1, .localhost, https://dashboard-eu-onenet.euprojects.net',
    cast=to_list()
)

# Set cronjobs here

CRONJOBS = [
    (
        '0 0 */{} * *'.format(number_of_days),
        'anomaly_detection.access_logs_modeling.anomaly_detection_job'
    ),
    (
        '*/{} * * * *'.format(batch_minutes),
        'anomaly_detection.access_logs_modeling.prediction_job'
    ),
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_crontab',
    'elastic.config.ElasticSearchConfig',
    'anomaly_detection',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'
LOGIN_REDIRECT_URL = "home"   # Route defined in app/urls.py
LOGOUT_REDIRECT_URL = "home"  # Route defined in app/urls.py
TEMPLATE_DIR = os.path.join(
    CORE_DIR, "core/templates")  # ROOT dir for templates

# TO-DO: Need to add the domain name here 
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200", "https://dashboard-eu-onenet.euprojects.net", "http://127.0.0.1:8000",
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
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

WSGI_APPLICATION = 'core.wsgi.application'

# Logging Configuration
# https://docs.djangoproject.com/en/3.1/topics/logging/#configuring-logging

# get all installed app names (including Django and main project's app)
APP_NAMES = [app.split('.')[0]
             for app in INSTALLED_APPS if not app.startswith('django.')]
APP_NAMES.append('django')
APP_NAMES.append(WSGI_APPLICATION.split('.')[0])
APP_NAMES.append('data_utilities')

# set a logger configuration for each app installed
LOGGERS = {}
for app in APP_NAMES:
    LOGGERS[app] = {
        'handlers': ['console', 'file'],
        'level': 'DEBUG',
        'propagate': True,
    }

# set higher log level for the 'django' app to exclude noisy logs
LOGGERS['django']['level'] = 'WARNING'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(levelname)s | %(funcName)s | %(name)s | %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 25,  # 25MB
            'backupCount': 10,
            'formatter': 'simple',
            'filename': BASE_DIR.child('logs').child('onenet_dashboard.log'),
        },
    },
    'loggers': LOGGERS
}


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
# TO DO: it needs to be changed for production cases
DATABASES = {
    'default': get_config(
        'DATABASE_URL',
        'sqlite:///' + BASE_DIR.child('db.sqlite3'),
        cast=db_url
    ),
    'postgres': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_config('DB_NAME', 'backend_db'),
        'USER': get_config('DB_USER', 'postgres'),
        'PASSWORD': get_config('DB_PASSWORD', 'postgres'),
        'HOST': get_config('DB_HOST', 'postgres-service'),
        'PORT': get_config('DB_PORT', '5432')
    }
}

# Define Database Routers:
DATABASE_ROUTERS = ['routers.db_routers.UserRouter', 'routers.db_routers.PredictionsRouter']

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },

]

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=30),
}

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

#############################################################
# SRC: https://devcenter.heroku.com/articles/django-assets

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(CORE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(CORE_DIR, 'core/static'),
)
#############################################################
#############################################################
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
