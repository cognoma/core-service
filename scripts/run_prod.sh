#!/bin/bash -x

# Application is configured to run under Supervisord, which in turn monitors
# the Gunicorn web server
supervisord -c /code/config/prod/supervisord.conf
