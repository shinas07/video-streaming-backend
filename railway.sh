#!/bin/sh

# Apply migrations
python manage.py migrate

# Start the application
PORT=${PORT:-8000}
gunicorn video_streaming.wsgi:application --bind 0.0.0.0:$PORT