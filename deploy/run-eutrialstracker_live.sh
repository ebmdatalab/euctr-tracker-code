#!/usr/bin/env bash

cd /var/www/eutrialstracker_live/euctr

export $(cat .env) && exec ../venv/bin/gunicorn euctr.wsgi -c ../deploy/gunicorn-eutrialstracker_live.conf.py  
