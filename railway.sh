#!/bin/sh

# Run migrations
python manage.py migrate

# Start Django
gunicorn video_streaming.wsgi:application --bind 0.0.0.0:8000

