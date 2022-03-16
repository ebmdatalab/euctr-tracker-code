# -*- coding: utf-8 -*-
from urllib.parse import urlencode
from functools import partial
from collections import OrderedDict
from datetime import date, timedelta
from scrapy.spiders import Rule
from scrapy.spiders import CrawlSpider
from scrapy.linkextractors import LinkExtractor
from crawl.parser import parse_record, trial_errback


# Module API

class Spider(CrawlSpider):

    # Public

    name = 'euctr'
    allowed_domains = ['clinicaltrialsregister.eu']

    def __init__(self, conf=None, conn=None, date_from=None, date_to=None, query=None):

        # Save conf/conn
        self.conf = conf
        self.conn = conn

        # Make start urls
        self.start_urls = _make_start_urls(
                prefix='https://www.clinicaltrialsregister.eu/ctr-search/search',
                date_from=date_from, date_to=date_to, query=query)

        # Make rules
        self.rules = [
            Rule(
                LinkExtractor(
                    allow=r'ctr-search/trial/[\d-]+/[\w]+',
                    deny=r'results$'
                ),
                callback=parse_record,
                errback=trial_errback
            ),
            Rule(
                LinkExtractor(
                    allow=r'page=\d+',
                    restrict_css='[accesskey=n]'
                ),
                process_links=partial(_process_links, self.start_urls)
            ),
        ]

        # Inherit parent
        super(Spider, self).__init__()


# Internal

def _make_start_urls(prefix, date_from=None, date_to=None, query=None):
    """ Return start_urls.
    """
    q = OrderedDict()
    q['query'] = query or ""
    if date_from:
        q['dateFrom'] = date_from
    if date_to:
        q['dateTo'] = date_to
    return [prefix + '?' + urlencode(q)]


def _process_links(start_urls, links):
    result = []
    for link in links:
        link.url = '&page='.join([start_urls[0], link.url.split('=')[-1]])
        result.append(link)
    return result
