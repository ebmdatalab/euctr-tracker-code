#!/bin/sh

service supervisor restart

if nginx -t
then
    service nginx stop 
    # TODO clear correct cache if have multiple environments
    rm -fr /var/cache/nginx/eutrialstracker_live/* 
    service nginx start
fi


