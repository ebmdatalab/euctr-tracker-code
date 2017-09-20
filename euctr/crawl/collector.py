# -*- coding: utf-8 -*-
from scrapy.crawler import CrawlerProcess
from .spider import Spider


# Module API

def collect(conf, conn, date_from=None, date_to=None):
    process = CrawlerProcess(conf['SCRAPY_SETTINGS'])
    process.crawl(Spider, conn=conn, date_from=date_from, date_to=date_to)
    process.start()