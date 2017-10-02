#!/bin/sh

. /etc/profile.d/eutrialstracker_live.sh
cd /var/www/eutrialstracker_live/euctr-tracker-data

WHEN=`date -d "yesterday 13:00" '+%Y-%m-%d'`

LOG_DIR=/var/www/eutrialstracker_live
mkdir -p LOG_DIR
LOG_FILE=$LOG_DIR/crawl-$WHEN.log

echo "Crawling up to $WHEN" >>$LOG_FILE
echo "=========================" >>$LOG_FILE
echo >>$LOG_FILE

./manage.py run_crawler 2004-01-01 $WHEN >>$LOG_FILE

