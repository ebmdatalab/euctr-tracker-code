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


from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify

TRIALS_CSV_FILE = '../../euctr-tracker-data/trials.csv'
TRIALS_META_FILE = '../../euctr-tracker-data/trials.csv.json'
PAPER_CSV_FILE = '../../euctr-tracker-data/paper_query.csv'

class Command(BaseCommand):
    help = 'Fetches trials data from OpenTrials PostgredSQL database and saves to trials.csv'

    def handle(self, *args, **options):
        verbosity = int(options['verbosity'])

        opentrials_db = os.environ['EUCTR_OPENTRIALS_DB']
        conn = psycopg2.connect(opentrials_db)
        cur = conn.cursor()

        # Find out the start date of current scrape.
        cur.execute("""select date(max(meta_updated)) from euctr""")
        scrape_date = cur.fetchone()[1]
        if verbosity > 1:
            print("Scrape start date:", scrape_date)

        # Date for reporting to be due has cutoff is 1 year (365 days) (by law,
        # trials must report a year after finishing) plus 4 weeks (28 days)
        # allowance (it takes that long for submissions to enter register)
        due_date_cutoff = scrape_date - datetime.timedelta(days=365 + 28)
        if verbosity > 1:
            print("Due date cutoff:", due_date_cutoff)

        # Generate the CSV file we later use in the web application
        query = open("euctr/management/commands/opentrials-to-csv.sql").read()
        params = { 'due_date_cutoff': due_date_cutoff }
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
                    ('scrape_date', scrape_date.isoformat()),
                    ('due_date_cutoff', due_date_cutoff.isoformat()),
                    ('got_from_db', datetime.datetime.now().isoformat())
                ])
                f.write(json.dumps(out, indent=4, sort_keys=True))
        else:
            if verbosity > 1:
                print("No changes, not updating meta file")
