#!/bin/sh

# Install missing OpenCV dependencies
apt-get update && apt-get install -y libgl1-mesa-glx

# Run migrations (optional)
python manage.py migrate

# Start Django
gunicorn video_streaming.wsgi:application --bind 0.0.0.0:$PORT
