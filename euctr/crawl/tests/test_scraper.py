import tempfile
import psycopg2

from django.test import SimpleTestCase
import datetime
import shutil
import testing.postgresql
from pathlib import Path
import subprocess
import psycopg2.extras


def crawl_report(db, registry_id):
    # We run the crawler in a subprocess, as this is the neatest way
    # to deal with restarting a Twisted reactor..
    with tempfile.TemporaryFile('r+') as f:
        subprocess.check_call(
            ['./manage.py',
             'run_crawler',
             '--query=' + registry_id,
             '--config=crawl.base.test_config',
             '--db=' + db],
            stdout=f,
            stderr=f
        )
        f.seek(0)
        output = f.read()
        assert "['cached']" in output, output + "\n(should be a fixture)"


def query(db, sql, params):
    conn = psycopg2.connect(db)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(sql, params)
    return cur


def setup_response(desired_gzipped_response):
    fixture_dir = Path(
        'crawl/tests/fixtures/euctr/4f/'
        '4ff2c188ce8d0558bf49ce65ba607b1a84e35f95')
    shutil.copyfile(
        fixture_dir / desired_gzipped_response,
        fixture_dir / 'response_body')


class ScrapingTestCase(SimpleTestCase):
    def test_fields_are_nulled(self):
        """When a field has a value which is absent in a future scrape, its
        value should be nulled in the database.
        """
        # Mocking a source page where a field subsequently disappears
        # involves some acrobatics:
        #
        # Because the scrapy framework uses Twisted, standard mocking
        # approaches that stub `requests` (for example) don't work.
        # Instead, we use scrapy's own HTTPCACHE functionality, which
        # is enabled in the `test_config` configuration passed to the
        # crawler management command in `crawl_report` (above).
        #
        # The cache key is a fingerprint of the request URL. Given the
        # scraper works by fetching an index page for a registry and
        # then following per-country links, the fingerprint of the
        # final per-country page that we want to test cannot be
        # predicted by the entry point for a scrape. Therefore, the
        # workflow for generating the fixtures used below is:
        #
        # * Run the scrape once
        # * Observe the files that are created in the scrapy HTTP cache
        #    * Note that the response_body files are gzipped
        # * Grep these to locate the response_body we want to manipulate
        # * Make different versions of response_body that we copy into place for each test

        registry_id = '2015-000590-12'
        registry_id_with_country = "%s-DE" % registry_id
        trial_end_sql = ("SELECT date_of_the_global_end_of_the_trial "
                         "FROM euctr "
                         "WHERE eudract_number_with_country = %s")
        with testing.postgresql.Postgresql() as postgresql:
            # First scrape should get a date for the trial end
            db = postgresql.url()
            setup_response('response_body_date')
            crawl_report(db, registry_id)
            cur = query(db, trial_end_sql, [registry_id_with_country])
            scrape_date = cur.fetchone()[0]
            self.assertEqual(scrape_date, datetime.date(2015, 10, 5))

            # In the second scrape, there is no value here (it's
            # empty). This should be reflected in the database.
            setup_response('response_body_nodate')
            crawl_report(db, registry_id)
            cur = query(db, trial_end_sql, [registry_id_with_country])
            scrape_date = cur.fetchone()[0]
            self.assertEqual(scrape_date, None)
