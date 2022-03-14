#!/bin/bash

pip3 install --upgrade pip && pip3 install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000