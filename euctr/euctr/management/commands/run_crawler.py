import scrapy

from django.core.management.base import BaseCommand, CommandError

import crawl.spider

class Command(BaseCommand):
    help = 'Crawls EUCTR website and converts into a PostgreSQL database'

    def handle(self, *args, **options):
        process = scrapy.crawler.CrawlerProcess({
                'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
                })

        process.crawl(crawl.spider.Spider)
        process.start()

