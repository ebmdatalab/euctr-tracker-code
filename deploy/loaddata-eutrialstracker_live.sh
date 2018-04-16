#!/bin/bash

export GIT_SSH_COMMAND='ssh -i /var/www/eutrialstracker_live/ssh-keys/id_rsa_eutrialtracker_data'

. /etc/profile.d/eutrialstracker_live.sh

# get updates to sponsor name normalization spreadsheet in particular
cd /var/www/eutrialstracker_live/euctr-tracker-data
git pull -q
chown -R www-data:www-data .

# import data from any scrape, and update processed JSON files from it
cd /var/www/eutrialstracker_live/
. venv/bin/activate
cd euctr-tracker-code/euctr
./manage.py get_trials_from_db
git commit -qa --author="Cron <>" --message="Automatic commit from eutrialstracker-live-cron" || exit
git push -q

# The Django app itself sends a normalization-required message to the
# correct recipient
# TODO: uncomment this line after the paper has been published
# See https://github.com/ebmdatalab/euctr-tracker-code/issues/30
# NORMALIZE_MESSAGE=$(./manage.py update_trials_json)

if [[ ! -z "$NORMALIZE_MESSAGE" ]]; then
    cd /var/www/eutrialstracker_live/euctr-tracker-data
    # exit if no changes during commit, so doesn't restart services if
    # that's the case
    git commit -qa --author="Cron <>" --message="Automatic commit from eutrialstracker-live-cron" || exit
    git push -q
    chown -R www-data:www-data .

    # restart web services so new data definitely picked up
    /var/www/eutrialstracker_live/euctr-tracker-code/deploy/restart-web-services.sh
fi
