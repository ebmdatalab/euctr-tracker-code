#!/bin/bash

export GIT_SSH_COMMAND='ssh -i /var/www/eutrialstracker_live/ssh-keys/id_rsa_eutrialtracker_data'

SOFTWARE_ROOT=/var/www/eutrialstracker_live
DATA_REPO=$SOFTWARE_ROOT/euctr-tracker-data
CODE_REPO=$SOFTWARE_ROOT/euctr-tracker-code

. /etc/profile.d/eutrialstracker_live.sh

# get updates to sponsor name normalization spreadsheet in particular
cd $DATA_REPO
git pull -q
chown -R www-data:www-data .

# Only proceed if there are uncommitted files. These should only exist
# as a result of crawl-and-dump-eutrialstracker_live.sh having been
# called, which is supposed to be once a month.
git add -A
changes=$(git diff-index HEAD)
if [[ ! -z "$changes" ]]; then
    # There are uncommitted changes: turn CSV into JSON
    # activate django environment
    . $SOFTWARE_ROOT/venv/bin/activate
    json_update_unfinished=$($CODE_REPO/euctr/manage.py update_trials_json)

    # The management command prints output to STDOUT (and emails
    # someone about it) if there are new rows requiring normalisation
    # in the sponsors CSV.
    if [[ -z $json_update_unfinished ]]; then
        # There are no rows requiring normalisation.
        git commit -qa --author="Cron <>" --message="Automatic commit from eutrialstracker-live-cron"
        git push -q
        chown -R www-data:www-data .
        # Restart web services so new data is loaded into memory
        $CODE_REPO/deploy/restart-web-services.sh
    fi
fi
