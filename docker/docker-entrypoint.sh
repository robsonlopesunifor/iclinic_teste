#!/bin/sh
set -e

python /source/manage.py migrate

exec "$@"