#!/bin/bash
set -e
python manage.py collectstatic --noinput
coverage run --branch --source='.' manage.py test
coverage report -m --omit=*migrations*,*__init__.py,*tests*
