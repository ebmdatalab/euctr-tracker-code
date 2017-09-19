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
SCRAPY_SETTINGS = {
    'SPIDER_MODULES': [
        'crawl.spider',
    ],
    'DOWNLOAD_DELAY': float(os.getenv('DOWNLOAD_DELAY', 1)),
    'AUTOTHROTTLE_ENABLED': True,
    'ITEM_PIPELINES': {
        'crawl.base.pipelines.Warehouse': 100,
    },
}


