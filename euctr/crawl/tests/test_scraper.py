import csv
import datetime
import os
import pathlib
import shutil
import subprocess
import tempfile

from django.test import SimpleTestCase
from django.test.utils import override_settings
from django.core.management import call_command
import psycopg2
import psycopg2.extras
import testing.postgresql


def crawl_report(db, registry_id):
    # We run the crawler in a subprocess, as this is the neatest way
    # to deal with restarting a Twisted reactor..
    with tempfile.TemporaryFile('r+') as f:
        subprocess.check_call(
            ['./manage.py',
             'run_crawler',
             '--query=' + registry_id,
             '--config=crawl.base.test_config',
             '--dburl=' + db],
            stdout=f,
            stderr=f
        )
        f.seek(0)
        output = f.read()
    assert "['cached']" in output, output + "\n(should be a fixture)"


def create_table(db):
    """Create a table according to the production schema
    """
    # We replace any roles with the `postgres` role used by the
    # `testing.postgresql` package.
    with open(pathlib.Path(__file__).parent.parent / 'schema.sql', 'r') as f:
        sql = f.read().replace("FROM euctr", "FROM postgres")
        sql = sql.replace("TO euctr", "To postgres")
        query(db, sql, [])


def insert_minimal_rows(db, rows):
    """Add the minimal columns we need to test date-related logic
    """
    for pk, meta_date in rows:
        sql = ("INSERT INTO euctr ("
               "  eudract_number, "
               "  eudract_number_with_country, "
               "  meta_created, "
               "  meta_updated) "
               "VALUES ("
               "  %s, %s, %s, %s)")
        query(db, sql, [pk, pk, meta_date, meta_date])


def query(db, sql, params):
    conn = psycopg2.connect(db)
    conn.autocommit = True
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(sql, params)
    return cur


def setup_response(desired_gzipped_response):
    fixture_dir = (
        'crawl/tests/fixtures/euctr/4f/'
        '4ff2c188ce8d0558bf49ce65ba607b1a84e35f95')
    shutil.copyfile(
        os.path.join(fixture_dir, desired_gzipped_response),
        os.path.join(fixture_dir, 'response_body'))


def setup_csv_fixture():
    """Create an empty file which can be written to by CSV creation
    command
    """
    with tempfile.NamedTemporaryFile() as f:
        f.write(b"")
        return f.name


# Setting up a temp file in package namespace means it's not
# garbage-collected until after the tests are run, meaning we can use
# it throughout the tests
f = tempfile.NamedTemporaryFile()
f.write(b"")

TEST_SETTINGS = {
    'SOURCE_CSV_FILE': f.name
}


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
        # * Make different versions of response_body that we copy into place
        #   for each test

        registry_id = '2015-000590-12'
        registry_id_with_country = "%s-DE" % registry_id
        trial_end_sql = ("SELECT "
                         "meta_updated, date_of_the_global_end_of_the_trial "
                         "FROM euctr "
                         "WHERE eudract_number_with_country = %s")
        with testing.postgresql.Postgresql() as postgresql:
            # testing.postgresql creates a temporary postgres database
            # and drops it again when the context is exited
            db = postgresql.url()
            create_table(db)

            # First scrape should get a date for
            # the trial end
            setup_response('response_body_date')
            crawl_report(db, registry_id)
            cur = query(db, trial_end_sql, [registry_id_with_country])
            res = cur.fetchone()
            self.assertEqual(res[0].date(), datetime.date.today())
            self.assertEqual(res[1], datetime.date(2015, 10, 5))

            # In the second scrape, there is no value here (it's
            # empty). This should be reflected in the database.
            setup_response('response_body_nodate')
            crawl_report(db, registry_id)
            cur = query(db, trial_end_sql, [registry_id_with_country])
            res = cur.fetchone()
            self.assertEqual(res[0].date(), datetime.date.today())
            self.assertEqual(res[1], None)

    @override_settings(**TEST_SETTINGS)
    def test_get_trials_from_db(self):
        registry_id = '2015-000590-12'
        with testing.postgresql.Postgresql() as postgresql:
            # testing.postgresql creates a temporary postgres database
            # and drops it again when the context is exited
            db = postgresql.url()
            create_table(db)
            setup_response('response_body_nodate')
            crawl_report(db, registry_id)

            # Now convert the database contents to a CSV
            call_command('get_trials_from_db', dburl=db)
            rows = list(csv.reader(open(TEST_SETTINGS['SOURCE_CSV_FILE'], "r")))
            self.assertEqual(
                rows[0],
                ['trial_id', 'number_of_countries', 'min_end_date',
                 'max_end_date', 'comp_date', 'has_results', 'includes_pip',
                 'exempt', 'single_blind', 'rare_disease', 'phase',
                 'bioequivalence_study', 'health_volunteers', 'trial_status',
                 'any_terminated', 'all_terminated', 'results_expected',
                 'all_completed_no_comp_date', 'sponsor_status', brexit_excluded,
                 'name_of_sponsor',
                 'trial_title',
                 'trial_url',
                 'comp_date_while_ongoing', 'contains_non_eu', 'only_non_eu'])
            self.assertEqual(
                rows[1],
                ['2015-000590-12', '1', '',
                 '', '0', '0', '0',
                 '0', '0', '0', '3',
                 '0', '0', '1',
                 '0', '0', '0',
                 '1', '1',
                 'Novartis Pharma GmbH', 'A 24-month multi-center, open-label, randomized, controlled study to evaluate the evolution of renal function in maintenance liver transplant recipients receiving either RAD001 (everolimus) plus reduc...',
                 'https://www.clinicaltrialsregister.eu/ctr-search/search?query=2015-000590-12',
                 '0', '0', '0'])

    @override_settings(**TEST_SETTINGS)
    def test_trial_removed_when_not_seen_for_a_while(self):
        with testing.postgresql.Postgresql() as postgresql:
            # testing.postgresql creates a temporary postgres database
            # and drops it again when the context is exited
            db = postgresql.url()
            create_table(db)
            # This CSV contains four rows
            fixture_data = [
                ['to_expire', '2000-01-01'],
                ['to_keep_1', '2000-03-05'],
                ['to_keep_2', '2000-04-01'],
                ['to_keep_3', '2000-05-01']
            ]
            insert_minimal_rows(db, fixture_data)
            call_command('get_trials_from_db', dburl=db)
            rows = list(
                csv.reader(open(TEST_SETTINGS['SOURCE_CSV_FILE'], "r")))
            self.assertEqual(len(rows), 4)  # including header
            self.assertNotIn('to_expire', [x[0] for x in rows])

    @override_settings(**TEST_SETTINGS)
    def test_trial_kept_when_not_seen_for_a_while_but_few_scrapes(self):
        with testing.postgresql.Postgresql() as postgresql:
            # testing.postgresql creates a temporary postgres database
            # and drops it again when the context is exited
            db = postgresql.url()
            create_table(db)
            # This CSV contains four rows
            fixture_data = [
                ['not_to_expire', '2000-01-01'],
                ['to_keep_3', '2000-05-01']
            ]
            insert_minimal_rows(db, fixture_data)
            call_command('get_trials_from_db', dburl=db)
            rows = list(
                csv.reader(open(TEST_SETTINGS['SOURCE_CSV_FILE'], "r")))
            self.assertEqual(len(rows), 3)  # including header
            self.assertIn('not_to_expire', [x[0] for x in rows])
