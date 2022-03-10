# -*- coding: utf-8 -*-
from scrapy.crawler import CrawlerProcess
from .spider import Spider

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Module API

def collect(conf, conn, date_from=None, date_to=None, query=None):
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer_provider().get_tracer(__name__)

    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter())
    )

    process = CrawlerProcess(conf['SCRAPY_SETTINGS'])
    process.crawl(Spider, conf=conf, conn=conn, date_from=date_from, date_to=date_to, query=query)
    process.start()
