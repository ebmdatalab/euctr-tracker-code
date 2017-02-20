#!/usr/bin/env bash

cd /var/www/eutrialstracker_live

export $(cat .env) && exec venv/bin/gunicorn config.wsgi -c deploy/gunicorn-eutrialstracker_live.conf.py  
