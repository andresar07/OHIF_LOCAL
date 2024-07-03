#!/bin/bash

if [ ! -n "$NUM_WORKERS" ]; then
  export NUM_WORKERS=4
fi

if [ ! -n "$NUM_THREADS" ]; then
  export NUM_THREADS=10
fi

python manage.py migrate


printenv



if [ "$GUNICORN_ASYNC_ENABLED" = "True" ]; then
  echo "INFO: Using gevent workers type"  
  gunicorn --workers=${NUM_WORKERS} --worker-class='gevent' --timeout=0  --bind=0.0.0.0:8000 --log-level='warning' key_images_back.wsgi
else
  echo "INFO: Using sync workers type"  
  gunicorn --workers=${NUM_WORKERS} --threads=${NUM_THREADS} --timeout=0 --bind=0.0.0.0:8000 --log-level='warning' key_images_back.wsgi
fi  
