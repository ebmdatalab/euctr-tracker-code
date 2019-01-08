import scrapy
import dataset
import importlib

from django.core.management.base import BaseCommand, CommandError

import crawl.collector
import crawl.base.helpers

class Command(BaseCommand):
    help = 'Crawls EUCTR website and converts into a PostgreSQL database'

    def add_arguments(self, parser):
        parser.add_argument('--query', type=str, default=None)
        parser.add_argument('--dburl', type=str, default=None)
        parser.add_argument('--config', type=str, default='crawl.base.config')
        parser.add_argument('date_from', nargs='?', type=str)
        parser.add_argument('date_to', nargs='?', type=str)

    def handle(self, *args, **options):
        config_module = importlib.import_module(options['config'])

        conf = crawl.base.helpers.get_variables(config_module, str.isupper)

        conn = {
            'warehouse': dataset.connect(options['dburl'] or crawl.base.config.WAREHOUSE_URL),
        }

        crawl.collector.collect(conf, conn, options['date_from'], options['date_to'], options['query'])
