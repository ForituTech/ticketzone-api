"""
Django settings for eticketing_api project.

Generated by 'django-admin startproject' using Django 4.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
from pathlib import Path

from corsheaders.defaults import default_headers

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.environ["DEBUG"]))

ALLOWED_HOSTS = [os.environ["ALLOWED_HOSTS"]]

API_VERSION_STRING = "v1"
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "storages",
    "rest_framework",
    "django_filters",
    "core",
    "events",
    "payments",
    "tickets",
    "partner",
    "drf_yasg",
    "django_celery_results",
    "notifications",
    "owners",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "eticketing_api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "eticketing_api.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
if os.environ.get("ENV") == "dev":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": os.environ["POSTGRES_DB"],
            "USER": os.environ["POSTGRES_USER"],
            "PASSWORD": os.environ["POSTGRES_PASSWORD"],
            "HOST": os.environ["POSTGRES_SERVER"],
            "PORT": os.environ["POSTGRES_PORT"],
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
        }
    }


if os.environ.get("GITHUB_WORKFLOW"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "github_actions",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "HOST": "127.0.0.1",
            "PORT": "5432",
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Nairobi"

USE_I18N = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

SITE_ROOT = os.path.join(os.path.dirname(__file__), "..")
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(SITE_ROOT)

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(os.path.dirname(__file__), "..", "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ],
        },
    }
]

TEMPLATE_LOADERS = (
    "django.template.loaders.app_directories.Loader",
    "django.template.loaders.filesystem.Loader",
)

# Parse database configuration from $DATABASE_URL
import dj_database_url

prod_db = dj_database_url.config(conn_max_age=500)
DATABASES["default"].update(prod_db)

# Celery
CELERY_RESULT_BACKEND = "django-db"
CELERY_BROKER_URL = os.environ["BROKER_URL"]

# EMail
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = "nellymogesh2@gmail.com"
EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


PUSHER_INSTANCE_ID = "test"
PUSHER_SECRET_KEY = "test"

AFRICAS_TALKING_USERNAME = "test"
AFRICAS_TALKING_KEY = "test"

DEFAULT_TICKET_TEMPLATE = "tickets/templates/ticket.html"
TICKET_EMAIL_TITLE = "Your ticket is here :) !"
TICKET_EMAIL_BODY = "Hi {} :), your ticket is here! The attachment on this email has all the relevant details"

REMINDER_SMS = "Hi {} :), just reminding you that {} is in the next 24 hrs ! Wohoo!"

POST_RECONCILIATION_MESSAGE = "HI {}. Your weekly reconciliation has just completed. Your total balance comes out to {}"

POST_PARTNER_PERSON_CREATE_EMAIL_TITLE = "Ticketzone Account Details"
POST_PARTNER_PERSON_CREATE_EMAIL = (
    "Hi {} your Tickezone credentials are:\n"
    "Username: {}, password: {} \n"
    "We would recommend you reset your password after login for safety purposes"
)

CORS_ALLOWED_ORIGIN_REGEXES = [r"^http.*$"]
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]
CORS_URLS_REGEX = r"^.*$"
CORS_ALLOW_HEADERS = list(default_headers)

AUTH_HEADER = "HTTP_AUTHORIZATION"

if os.environ.get("ENV") != "dev" and not os.environ.get("GITHUB_WORKFLOW", None):
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
else:
    DEFAULT_FILE_STORAGE = "inmemorystorage.InMemoryStorage"

AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_STORAGE_BUCKET_NAME = os.environ["AWS_STORAGE_BUCKET_NAME"]
AWS_QUERYSTRING_AUTH = False
BASE_S3_URL = os.environ["BASE_S3_URL"]

if os.environ.get("ENV") != "dev" and not os.environ.get("GITHUB_WORKFLOW", None):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True

CELERY_MAIN_QUEUE = "main_queue"
CELERY_NOTIFICATIONS_QUEUE = "notifications-queue"
