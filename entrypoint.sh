#!/bin/sh

python manage.py makemigrations
python manage.py migrate

python manage.py runserver 0.0.0.0:8000 &

exec python ./chat/socket_server.py 0.0.0.0