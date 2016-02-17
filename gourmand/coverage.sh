#!/bin/bash
set -e
python manage.py collectstatic --noinput
OPBEAT_DISABLE_SEND=true coverage run --branch --source='.' manage.py test
coverage report -m --omit=*migrations*,*__init__.py,*tests*
