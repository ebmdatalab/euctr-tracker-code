import subprocess
import os

from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify

TRIALS_CSV_FILE = '../data/trials.csv'

class Command(BaseCommand):
    help = 'Fetches trials data from OpenTrials PostgredSQL database and saves to trials.csv'

    def handle(self, *args, **options):
        opentrials_db = os.environ['OPENTRIALS_DB']
        params = [ 'psql', '--quiet', '-f', '../data/opentrials-to-csv.sql', '-o', TRIALS_CSV_FILE, '--dbname', opentrials_db ]
        print(params)
        subprocess.call(params)


