#!/bin/bash
set -e
OPBEAT_DISABLE_SEND=true coverage run --source='.' manage.py test
coverage report -m --omit=*migrations*,*__init__.py,*tests*
