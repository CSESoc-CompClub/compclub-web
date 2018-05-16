from settings import *
import os

SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = False

DB_PATH=os.environ['DB_PATH']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_PATH,
    }
}
