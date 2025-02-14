"""
Django settings for email_automation project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os
import json
import base64
import environ
import dj_database_url
from pathlib import Path
from email.headerregistry import Address
from logging.handlers import SysLogHandler

from google.oauth2 import service_account


env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(env('DEBUG')))

cloud_platform = os.environ.setdefault('CLOUD_PLATFORM', '')

if cloud_platform in ['DIGITAL_OCEAN', 'VERCEL']:
    # since the firebase_cred cannot be uploaded manually 
    # https://www.digitalocean.com/community/questions/how-to-upload-a-secret-credential-file
    firebase_cred = env('FIREBASE_ENCODED')
    decoded_bytes = base64.b64decode(firebase_cred)
    decoded_json = json.loads(decoded_bytes.decode('utf-8'))
  
    with open(env('FIREBASE_CRED_PATH'), 'w') as f:
        json.dump(decoded_json, f, indent=4)


# SECURITY WARNING: keep the secret key used in production secret!
if DEBUG:
    SECRET_KEY = env.get_value('SECRET_KEY', default='django-insecure-ksg!i&r49#t+x6*f^v#glkvhg_nfb^24r%l7im#ti-(it!5(y6')

else:
    SECRET_KEY = env.get_value('PORD_SECRET_KEY')

if DEBUG:
    ALLOWED_HOSTS = ['blast.specialdispatcher.store']

else:
    ALLOWED_HOSTS = env('ALLOWED_PROD_HOSTS').replace(' ', '').split(',')


if DEBUG:
    DOMAIN = 'http://localhost:8000'

else:
    DOMAIN = env('DOMAIN')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    #3rd party
    'encrypted_model_fields',
    'tailwind',
    'theme',
    'corsheaders',
    'django_celery_beat',
    'django_browser_reload',

    # my apps
    'automail',
    'user',
    # 'terms',
    'blog'

]

if DEBUG:
    FIELD_ENCRYPTION_KEY = env.get_value('FIELD_ENCRYPTION_KEY')

else:
    FIELD_ENCRYPTION_KEY = env.get_value('PROD_FIELD_ENCRYPTION_KEY')

# # Decode the base64-encoded string to bytes with UTF-8 encoding
# FIELD_ENCRYPTION_KEY = base64.b64decode(FIELD_ENCRYPTION_KEY_str)

LOGIN_URL = '/user/login/'

AUTH_USER_MODEL = "user.User" 

TAILWIND_APP_NAME = 'theme'

RATELIMIT_VIEW = 'email_automation.views.rate_limiter_view'

INTERNAL_IPS = [
    "127.0.0.1",
]

if DEBUG:
    CELERY_BROKER_URL = 'redis://127.0.0.1:6379'

else: 
    CELERY_BROKER_URL = env('REDIS_PROD_HOST').strip()


CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'

CELERYBEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'
CELERY_IMPORTS = ['utils.tasks',]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', #whitenoise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    "django_browser_reload.middleware.BrowserReloadMiddleware", # reload
    
    'django_ratelimit.middleware.RatelimitMiddleware',
    'email_automation.middlewares.RateLimitJsonResponseMiddleware',
    # 'email_automation.middlewares.TimezoneMiddleware',

    'email_automation.middlewares.FileUploadMiddleware',

]

ROOT_URLCONF = 'email_automation.urls'


if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # This is only for development
    # EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
   
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # for production

    EMAIL_HOST = env('EMAIL_HOST')
    EMAIL_PORT = 465

    EMAIL_HOST_USER = env('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

    DEFAULT_FROM_EMAIL = Address(display_name="AtMailWin", addr_spec=EMAIL_HOST_USER)

    # EMAIL_USE_TLS = True
    EMAIL_USE_SSL = True

EMAIL_FROM_SIGNATURE = 'Best regards, Atmailwin Team'
EMAIL_FROM = 'info@atmailwin.com'
EMAIL_FROM_NAME = 'AtMailWin'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR.joinpath("templates"),
            BASE_DIR.joinpath("templates", "html", ),
            BASE_DIR.joinpath("templates", "html", "error"),
            BASE_DIR.joinpath("templates", "html", "authentication"),
            BASE_DIR.joinpath("templates", "html", "terms"),
            BASE_DIR.joinpath("templates", "html", "blog"),
            BASE_DIR.joinpath("templates", "html", "email-product"),
            BASE_DIR.joinpath("templates", "html", "email-product", "templates"),
            BASE_DIR.joinpath("templates", "html", "email-product", "campaign"),
            BASE_DIR.joinpath("templates", "html", "email-product", "configuration"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
               
                'email_automation.context_processors.secrets',
                
            ],
        'libraries':{
            'custom_tags': 'email_automation.templatetags.custom_tags',
            
            }
        },
    },
]

WSGI_APPLICATION = 'email_automation.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        },
        'OPTIONS': {
            "timeout": 20,
        }
    }

else:
    # DATABASES = {
    #         'default': {
    #             'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #             'NAME': env.get_value('POSTGRES_DATABASE'), # use env file
    #             'USER': env.get_value('POSTGRES_USER'),
    #             # 'PASSWORD': os.environ.get('PROD_DB_PASSWORD'),
    #             'PASSWORD': env.get_value('POSTGRES_PASSWORD'),
    #             'HOST': env.get_value('POSTGRES_HOST'),
    #             'PORT': '5432',
    #     }
    # }

    DATABASES  = {
                    'default':dj_database_url.config(default=env('POSTGRES_URL')),
                                   
                }
    DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'



CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"{env('REDIS_PROD_HOST')}/0" if not DEBUG else "redis://127.0.0.1:6379/0",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': env('REDIS_PASSWORD') if not DEBUG else ""
        },
        'TIMEOUT': 300,  # Set the cache timeout in seconds
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATICFILES_DIRS = [
    BASE_DIR.joinpath("templates"),
]


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR.joinpath('staticfiles', 'static')
STATICFILES_DIRS = [
                        BASE_DIR.joinpath('templates'),
                        BASE_DIR.joinpath('templates', 'js'),
                        BASE_DIR.joinpath('templates', 'css'),
                        BASE_DIR.joinpath('templates', 'assets'),
                    ]


# if not DEBUG:
    # STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


MEDIA_ROOT = BASE_DIR.joinpath('media')

if DEBUG:
    MEDIA_URL = '/media/'
    MEDIA_DOMAIN = 'http://localhost:8000'
   

    # DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    # GS_BUCKET_NAME = env("BUCKET_NAME")
    # GS_PROJECT_ID = env("PROJECT_ID")
    # GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    #     BASE_DIR.joinpath(env("FIREBASE_CRED_PATH"))
    # )
    # GS_DEFAULT_ACL = "publicRead"  # Optional: Set ACL for public access
    # GS_QUERYSTRING_AUTH = True  # Optional: Enable querystring authentication


else:
    MEDIA_URL = '/media/'

    # Define the storage settings for media files
    DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    GS_BUCKET_NAME = env("BUCKET_NAME")
    GS_PROJECT_ID = env("PROJECT_ID")
    GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
        BASE_DIR.joinpath(env("FIREBASE_CRED_PATH"))
    )
    GS_DEFAULT_ACL = "publicRead"  # Optional: Set ACL for public access
    GS_QUERYSTRING_AUTH = True  # Optional: Enable querystring authentication
    GS_FILE_OVERWRITE = False # prevent overwriting

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '[contactor] %(levelname)s %(asctime)s %(message)s'
        },
    },
    'handlers': {
        # Send all messages to console
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        
        'celery': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },

        # Send info messages to syslog
        # 'syslog':{
        #     'level':'INFO',
        #     'class': 'logging.handlers.SysLogHandler',
        #     'facility': SysLogHandler.LOG_LOCAL2,
        #     'address': '/dev/log',
        #     'formatter': 'verbose',
        # },
        # Warning messages are sent to admin emails
        'mail_admins': {
            'level': 'WARNING',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        # critical errors are logged to sentry
        # 'sentry': {
        #     'level': 'ERROR',
        #     'filters': ['require_debug_false'],
        #     'class': 'raven.contrib.django.handlers.SentryHandler',
        # },
    },
    'loggers': {
        # This is the "catch all" logger
        '': {
            'handlers': ['console', 'mail_admins', 'celery'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
