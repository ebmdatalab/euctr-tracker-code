#!/usr/bin/env bash

service supervisor restart

# TODO clear correct cache if have multiple instances
nginx -t && service nginx stop && rm -fr /var/cache/nginx/eutrialstracker_live/* && service nginx start


