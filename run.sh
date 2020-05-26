#!/bin/bash
set -euo pipefail

# Entrypoint for production

# You may need to run python manage.py makemigrations manually to update the database first

# Create database
python manage.py migrate --no-input --run-syncdb

# roll up static files
python manage.py collectstatic --clear --no-input

# Compress and compile the stylesheets
python manage.py compress --force

# Clean up
find ./static -name "*.scss" -type f -delete
find ./static -type d -empty -delete

# Run gunicorn
gunicorn -c gunicorn.py wsgi:application &

# Run nginx
mkdir --parents /etc/nginx/
cp nginx.conf /etc/nginx/nginx.conf

service nginx start

tail -f /var/log/nginx/*.log
