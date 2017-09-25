# -*- coding: utf-8 -*-
import os
import logging
import logging.config

# Environment

EUCTR_DEBUG = os.environ.get('EUCTR_DEBUG', 'development')
if EUCTR_DEBUG == "yes":
    ENV = 'testing'
elif EUCTR_DEBUG == "no":
    ENV = 'production'
else:
    assert False, "yes or no for debug"
WAREHOUSE_URL = os.environ['EUCTR_OPENTRIALS_DB']

# Scrapy
CRAWLERA_APIKEY = os.getenv('EUCTR_CRAWLERA_APIKEY', None)
SCRAPY_SETTINGS = {
    'SPIDER_MODULES': [
        'crawl.spider',
    ],
    'DOWNLOAD_DELAY': float(os.getenv('DOWNLOAD_DELAY', 1)),
    'CONCURRENT_REQUESTS_PER_DOMAIN': 32,
    'CONCURRENT_REQUESTS': 10,

    #'AUTOTHROTTLE_ENABLED': True,
    #'AUTOTHROTTLE_TARGET_CONCURRENCY': 5,
    #'AUTOTHROTTLE_DEBUG': True,

    'RETRY_ENABLED': True,
    'RETRY_TIMES': 20,

    'ITEM_PIPELINES': {
        'crawl.base.pipelines.Warehouse': 100,
    },
    'DOWNLOADER_MIDDLEWARES': {'scrapy_crawlera.CrawleraMiddleware': 600},
    'CRAWLERA_ENABLED': CRAWLERA_APIKEY != None,
    'CRAWLERA_APIKEY': CRAWLERA_APIKEY
}


