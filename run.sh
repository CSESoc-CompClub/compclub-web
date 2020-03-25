#!/bin/bash
set -euo pipefail

# Entrypoint for production

# Create database
python manage.py migrate --run-syncdb

# roll up static files
python manage.py collectstatic

# Run gunicorn
gunicorn -c gunicorn.py wsgi:application &

# Run nginx
mkdir --parents /etc/nginx/
cp nginx.conf /etc/nginx/nginx.conf

service nginx start

tail -f /var/log/nginx/*.log
