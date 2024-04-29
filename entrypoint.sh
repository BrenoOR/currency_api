#!/bin/sh

# Execute migrations
python manage.py makemigrations
python manage.py migrate

python manage.py createsuperuser --noinput

# Init app
python manage.py runserver 0.0.0.0:8000 --noreload
