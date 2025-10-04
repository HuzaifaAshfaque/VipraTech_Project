#!/bin/sh
set -e

echo "Waiting for postgres..."
while ! nc -z postgres 5432; do
  echo "Postgres is unavailable - sleeping 1s"
  sleep 1
done

echo "Postgres is up! Applying migrations..."

# Ensure Django knows which settings to use
export DJANGO_SETTINGS_MODULE=djstripeinti.settings  # replace myproject with your Django project name

python manage.py migrate --noinput



echo "Starting Django server..."
exec "$@"
