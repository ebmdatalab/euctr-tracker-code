import datetime
import os
import tempfile

from google.cloud import storage
import psycopg2

from django.core.management.base import BaseCommand


def _safe_filename(filename):
    """
    Generates a safe filename that is unlikely to collide with existing objects
    in Google Cloud Storage.
    ``filename.ext`` is transformed into ``filename-YYYY-MM-DD-HHMMSS.ext``
    """
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%M%S")
    basename, extension = filename.rsplit('.', 1)
    return "{0}-{1}.{2}".format(basename, now, extension)


def upload_file(filename_to_upload):
    """
    Uploads a file to a given Cloud Storage bucket and returns the public url
    to the new object.
    """
    filename = _safe_filename(filename_to_upload)
    client = storage.Client(project='ebmdatalab')
    bucket = client.bucket('euctr')
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename_to_upload)
    return filename


class Command(BaseCommand):
    help = ('Fetches trials data from OpenTrials PostgredSQL database and '
            'saves to trials.csv')

    def handle(self, *args, **options):
        opentrials_db = os.environ['EUCTR_OPENTRIALS_DB']
        conn = psycopg2.connect(opentrials_db)
        cur = conn.cursor()
        query = "COPY euctr TO STDOUT DELIMITER ',' CSV HEADER;"
        fname = os.path.join(tempfile.gettempdir(), 'euctr_dump.csv')
        # `touch` the file. This is so we can open it in `r+b` mode to
        # work around a google-bigquery-python bug
        with open(fname, 'a'):
            os.utime(fname, None)
        with open(fname, 'r+b') as f:
            cur.copy_expert(query, f)
        upload_file(fname)
