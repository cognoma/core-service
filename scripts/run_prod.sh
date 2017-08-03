#!/bin/bash -x
python manage.py collectstatic --no-input
python manage.py migrate -v3 --no-input

# Application is configured to run under Supervisord, which in turn monitors
# the Gunicorn web server
supervisord -c /code/config/prod/supervisord.conf
