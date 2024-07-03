#!/bin/bash

if [ ! -n "$NUM_WORKERS" ]; then
  export NUM_WORKERS=10
fi

if [ ! -n "$NUM_THREADS" ]; then
  export NUM_THREADS=4
fi

# The next command was comment while test
python manage.py migrate

printenv

if [ "$GUNICORN_ASYNC_ENABLED" = "True" ]; then
  echo "INFO: Using gevent workers type"  
  gunicorn --workers=${NUM_WORKERS} --worker-class='gevent' --timeout=0 --bind=0.0.0.0:8000 --log-level='warning' Annotations_back.wsgi
else
  echo "INFO: Using sync workers type"  
  gunicorn --workers=${NUM_WORKERS} --threads=${NUM_THREADS} --timeout=0 --bind=0.0.0.0:8000 --log-level='warning' Annotations_back.wsgi 
fi  
