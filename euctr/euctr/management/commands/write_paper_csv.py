import os
import psycopg2
import csv

from atomicwrites import atomic_write


from django.core.management.base import BaseCommand, CommandError

PAPER_CSV_FILE = '../../euctr-tracker-data/paper_query.csv'

class Command(BaseCommand):
    help = 'Fetches trials data from OpenTrials PostgreSQL database and saves to CSV for paper'

    def handle(self, *args, **options):
        verbosity = int(options['verbosity'])
        # Data as of paper date at
        # https://github.com/ebmdatalab/euctr-tracker-data/
        # tree/master/archive/euctr-dump-paper-2018-01-17.sq.zx
        opentrials_db = os.environ['EUCTR_OPENTRIALS_DB']
        conn = psycopg2.connect(opentrials_db)
        cur = conn.cursor()
        # Generate the CSV file we later use in the web application
        paper_query = open("euctr/management/commands/opentrials-to-paper-csv.sql").read()
        cur.execute(paper_query)
        with atomic_write(PAPER_CSV_FILE, overwrite=True) as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow([i[0] for i in cur.description])
            writer.writerows(cur)
