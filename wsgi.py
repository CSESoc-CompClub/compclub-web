from __future__ import unicode_literals
from django.core.wsgi import get_wsgi_application
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'settings_prod')
application = get_wsgi_application()
