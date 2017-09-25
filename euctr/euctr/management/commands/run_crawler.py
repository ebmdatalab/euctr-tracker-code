import scrapy
import dataset

from django.core.management.base import BaseCommand, CommandError

import crawl.collector
import crawl.base.helpers
import crawl.base.config

class Command(BaseCommand):
    help = 'Crawls EUCTR website and converts into a PostgreSQL database'

    def add_arguments(self, parser):
        parser.add_argument('--query', type=str, default=None)
        parser.add_argument('date_from', nargs='?', type=str)
        parser.add_argument('date_to', nargs='?', type=str)

    def handle(self, *args, **options):
        conf = crawl.base.helpers.get_variables(crawl.base.config, str.isupper)

        conn = {
            'warehouse': dataset.connect(crawl.base.config.WAREHOUSE_URL),
        }

        crawl.collector.collect(conf, conn, options['date_from'], options['date_to'], options['query'])
