#!/bin/sh

/usr/sbin/service supervisor restart

if /usr/sbin/nginx -t
then
    /usr/sbin/service nginx stop
    # TODO clear correct cache if have multiple environments
    rm -fr /var/cache/nginx/eutrialstracker_live/*
    /usr/sbin/service nginx start
fi
