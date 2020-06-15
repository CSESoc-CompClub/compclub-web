#!/bin/bash
set -euo pipefail

# Entrypoint for production

# Create database manually (to be safe)
# python manage.py makemigrations
# python manage.py migrate --no-input

# Clear old static folder
rm -r ./static || true
mkdir -p static

# roll up static files
python manage.py collectstatic --clear --no-input

# Compress and compile the stylesheets
python manage.py compress --force

# Compress the images
python manage.py compress_images ./static/website


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
