#!/bin/bash -x

python manage.py migrate -v3 --no-input
python manage.py runserver 0.0.0.0:8000
