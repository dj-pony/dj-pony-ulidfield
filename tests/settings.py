# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import
from pathlib import Path

import django

print(Path.cwd())

DEBUG = True
USE_TZ = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "**************************************************"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        # "NAME": ":memory:",
        "NAME": str(Path.cwd() / "ulidfield.db"),
        "TEST": {
            "NAME": str(Path.cwd() / "test_ulidfield.db"),
        }
    }
}

ROOT_URLCONF = "tests.urls"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "dj_pony.ulidfield",
    "tests.form_field",
    "tests.model_field",
]

SITE_ID = 1

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'loggers': {
#         # 'django': {
#         #     'handlers': ['console'],
#         #     'level': 'DEBUG',
#         #     'propagate': True,
#         # },
#         'django.db.backends': {
#             'handlers': ['console'],
#             'level': 'DEBUG',
#         }
#     },
# }

if django.VERSION >= (1, 10):
    MIDDLEWARE = ()
else:
    MIDDLEWARE_CLASSES = ()
