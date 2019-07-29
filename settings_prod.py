"""
Production settings.

Overrides default settings in settings.py
"""

import os

from settings import *  # noqa: F401, F403

SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = False

DB_PATH = os.environ['DB_PATH']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_PATH,
    }
}
