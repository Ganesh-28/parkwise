#!/usr/bin/env bash
set -o errexit

cd backend

python manage.py collectstatic --noinput
python manage.py migrate
python manage.py seed_data