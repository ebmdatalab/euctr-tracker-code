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

        # Find out the earliest date of current scrape.
        # The "count(*) > 100" part can be removed when
        # https://github.com/opentrials/opentrials/issues/821 is fixed
        cur.execute("""select count(*) as c, date(meta_updated) as d from euctr
                group by d having count(*) > 100 order by d limit 1""")
        scrape_date = cur.fetchone()[1]
        if verbosity > 1:
            print("Scrape start date:", scrape_date)

        # See if we have a clear new enough scrape. It takes maybe 4 days
        # for OpenTrials to do a full scrape. So if the scrape started more
        # than a week ago it's either:
        # a) already been fully logged so nothing to do
        # b) some new data has arrived, but not a full set - we don't want to mix in
        #    order to have a reasonable quality historical record
        # For now, give up. TODO: Fix scraper to run with reliable regularity.
        if scrape_date + datetime.timedelta(days=7) < datetime.date.today():
            # Abandoning import from database: Scrape started too long ago to use data for new history point
            return

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
