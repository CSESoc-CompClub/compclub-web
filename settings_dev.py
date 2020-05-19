"""Development settings."""

import os

from settings import *  # noqa: F401, F403

SECRET_KEY = 'development-only'
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),  # noqa: F405
    }
}
