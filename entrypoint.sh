#!/bin/sh

# Execute migrations
python manage.py makemigrations
python manage.py migrate

python manage.py createsuperuser --noinput

# Init app
uvicorn --host <your-machine-private-ip> --use-colors --env-file .env currency_api.asgi:application
