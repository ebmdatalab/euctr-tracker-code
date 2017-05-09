import subprocess
import os
import sys
import psycopg2
import csv
import datetime
import json
import collections

from atomicwrites import atomic_write


from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify

TRIALS_CSV_FILE = '../data/trials.csv'
TRIALS_META_FILE = '../data/trials.csv.json'

class Command(BaseCommand):
    help = 'Fetches trials data from OpenTrials PostgredSQL database and saves to trials.csv'

    def handle(self, *args, **options):
        opentrials_db = os.environ['EUCTR_OPENTRIALS_DB']
        conn = psycopg2.connect(opentrials_db)
        cur = conn.cursor()

        # Find out the earliest date of current scrape.
        # The "count(*) > 100" part can be removed when
        # https://github.com/opentrials/opentrials/issues/821 is fixed
        cur.execute("""select count(*) as c, date(meta_updated) as d from euctr
                group by d
                having count(*) > 100
                order by d limit 1""")
        scrape_date = cur.fetchone()[1]

        # Date for reporting to be due has cutoff is 1 year (365 days) (by law,
        # trials must report a year after finishing) plus 3 weeks (21 days)
        # allowance (it takes that long for submissions to enter register)
        due_date_cutoff = scrape_date - datetime.timedelta(days=365 + 21)
        print("Due date cutoff:", due_date_cutoff)

        with atomic_write(TRIALS_META_FILE, overwrite=True) as f:
            out = collections.OrderedDict([
                ('scrape_date', scrape_date.isoformat()),
                ('due_date_cutoff', due_date_cutoff.isoformat()),
                ('got_from_db', datetime.datetime.now().isoformat())
            ])
            f.write(json.dumps(out, indent=4, sort_keys=True))

            query = open("euctr/management/commands/opentrials-to-csv.sql").read()
            params = { 'due_date_cutoff': due_date_cutoff }
            cur.execute(query, params)

            with atomic_write(TRIALS_CSV_FILE, overwrite=True) as f:
                writer = csv.writer(f, lineterminator="\n")
                writer.writerow([i[0] for i in cur.description])
                writer.writerows(cur)



