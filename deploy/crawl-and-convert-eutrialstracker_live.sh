#!/bin/bash

set -eo pipefail

/var/www/eutrialstracker_live/euctr-tracker-code/deploy/crawl-eutrialstracker_live.sh
/var/www/eutrialstracker_live/euctr-tracker-code/deploy/convertdata-eutrialstracker_live.sh
