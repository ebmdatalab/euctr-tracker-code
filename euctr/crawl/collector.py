# -*- coding: utf-8 -*-
from scrapy.crawler import CrawlerProcess
from .spider import Spider


# Module API

def collect(conf, conn, date_from=None, date_to=None, query=None):
    process = CrawlerProcess(conf['SCRAPY_SETTINGS'])
    process.crawl(Spider, conf=conf, conn=conn, date_from=date_from, date_to=date_to, query=query)
    process.start()
