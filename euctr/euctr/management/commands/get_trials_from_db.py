import subprocess
import os
import psycopg2
import csv

from atomicwrites import atomic_write


from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify

TRIALS_CSV_FILE = '../data/trials.csv'

class Command(BaseCommand):
    help = 'Fetches trials data from OpenTrials PostgredSQL database and saves to trials.csv'

    def handle(self, *args, **options):
        opentrials_db = os.environ['EUCTR_OPENTRIALS_DB']
        conn = psycopg2.connect(opentrials_db)
        cur = conn.cursor()

        query = open("euctr/management/commands/opentrials-to-csv.sql").read()
        cur.execute(query)

        with atomic_write(TRIALS_CSV_FILE, overwrite=True) as f:
            writer = csv.writer(f)
            writer.writerow([i[0] for i in cur.description])
            writer.writerows(cur)
