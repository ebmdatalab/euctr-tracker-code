from datetime import date
import os
import tempfile
from google.cloud import bigquery
import psycopg2
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Fetches trials data from OpenTrials PostgredSQL database and saves to trials.csv'

    def handle(self, *args, **options):

        opentrials_db = os.environ['EUCTR_OPENTRIALS_DB']
        conn = psycopg2.connect(opentrials_db)
        cur = conn.cursor()
        client = bigquery.Client(project='ebmdatalab')
        dataset_id = 'euctr'
        table_id = 'euctr_{}'.format(date.today().strftime("%Y_%m_%d"))

        dataset_ref = client.dataset(dataset_id)
        table_ref = dataset_ref.table(table_id)
        job_config = bigquery.LoadJobConfig()
        job_config.source_format = bigquery.SourceFormat.CSV
        job_config.autodetect = True

        fname = os.path.join(tempfile.gettempdir(), 'euctr_dump.csv')
        query = "COPY euctr TO STDOUT DELIMITER ',' CSV HEADER;"
        # `touch` the file. This is so we can open it in `r+b` mode to
        # work around a google-bigquery-python bug
        with open(fname, 'a'):
            os.utime(fname, None)
        with open(fname, 'r+b') as f:
            cur.copy_expert(query, f)
            f.seek(0)
            job = client.load_table_from_file(
                f,
                table_ref,
                job_config=job_config)  # API request

            job.result()  # Waits for table load to complete.
            print('Loaded {} rows into {}:{}.'.format(
                job.output_rows, dataset_id, table_id))
