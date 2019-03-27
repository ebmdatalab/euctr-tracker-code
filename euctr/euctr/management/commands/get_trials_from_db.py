import subprocess
import os
import sys
import psycopg2
import csv
import datetime
import json
import collections
import hashlib

from atomicwrites import atomic_write

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify

TRIALS_CSV_FILE = settings.SOURCE_CSV_FILE
TRIALS_META_FILE = settings.SOURCE_META_FILE
PAPER_CSV_FILE = '../../euctr-tracker-data/paper_query.csv'

class Command(BaseCommand):
    help = 'Fetches trials data from OpenTrials PostgreSQL database and saves to trials.csv'

    def add_arguments(self, parser):
        default_db = os.environ.get('EUCTR_OPENTRIALS_DB', None)
        parser.add_argument('--dburl',
                            type=str,
                            default=default_db)

    def handle(self, *args, **options):
        verbosity = int(options['verbosity'])

        opentrials_db = options['dburl']
        conn = psycopg2.connect(opentrials_db)
        cur = conn.cursor()
        # Find out the start date of current scrape.
        cur.execute(
            "select date(meta_updated) from euctr "
            "group by meta_updated "
            "order by meta_updated desc limit 60")
        scrape_dates = [x[0] for x in cur.fetchall()]
        # Default to the oldest of the last 60 runs
        sufficiently_old = scrape_dates[-1]
        last_scrape_date = scrape_dates.pop(0)
        if verbosity > 1:
            print("Late scrape start date:", last_scrape_date)

        # sufficiently_old: the date that is both more than 60 days
        # ago *and* more than 2 scrapes old. We assume such trials not
        # longer exist. The hand-waving around 60 days and 2 scrapes
        # is because some trials apparently reappear. See #66 for
        # discussion and analysis.
        scrape_index = 0
        scrape_window = 3
        for d in scrape_dates:
            scrape_index += 1
            if d > (last_scrape_date - datetime.timedelta(days=60)):
                # Disregard dates in the last 2 months
                continue
            if scrape_index >= scrape_window:
                sufficiently_old = d
                break
        if scrape_index < scrape_window \
           or last_scrape_date == sufficiently_old:
            # There's not been enough scrapes to expire anything, so
            # expire nothing
            sufficiently_old = sufficiently_old - datetime.timedelta(days=1)
        if verbosity > 1:
            print("Will skip trials older than:", sufficiently_old)

        # Date for reporting to be due has cutoff is 1 year (365 days) (by law,
        # trials must report a year after finishing) plus 4 weeks (28 days)
        # allowance (it takes that long for submissions to enter register)
        due_date_cutoff = last_scrape_date - datetime.timedelta(days=365 + 28)
        if verbosity > 1:
            print("Due date cutoff:", due_date_cutoff)

        # Generate the CSV file we later use in the web application
        query = open("euctr/management/commands/opentrials-to-csv.sql").read()
        params = {
            'due_date_cutoff': due_date_cutoff,
            'sufficiently_old': sufficiently_old}
        cur.execute(query, params)
        before_hash = hashlib.sha512(open(TRIALS_CSV_FILE).read().encode("utf-8")).digest()
        with atomic_write(TRIALS_CSV_FILE, overwrite=True) as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow([i[0] for i in cur.description])
            writer.writerows(cur)
        after_hash = hashlib.sha512(open(TRIALS_CSV_FILE).read().encode("utf-8")).digest()

        # Update "got_from_db" only if there were changes in database
        # (to stop git history being contaminated)
        if before_hash != after_hash:
            if verbosity > 1:
                print("Changes being recorded in meta file")
            with atomic_write(TRIALS_META_FILE, overwrite=True) as f:
                out = collections.OrderedDict([
                    ('scrape_date', last_scrape_date.isoformat()),
                    ('due_date_cutoff', due_date_cutoff.isoformat()),
                    ('got_from_db', datetime.datetime.now().isoformat())
                ])
                f.write(json.dumps(out, indent=4, sort_keys=True))
        else:
            if verbosity > 1:
                print("No changes, not updating meta file")
